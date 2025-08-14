# models/custom_qwen.py
# Qwen chat/completions ile tool-calling yapan çoklu tool destekli özel model adaptörü

import json
from typing import Any, Dict, Iterable, List, Optional

import requests

from app_tools import TOOL_SCHEMAS
from app_tools.current_tools import (
    _get_customer_details_impl,
    _get_card_summary_info_impl,
)
from app_tools.analysis_tools import analyze_credit_offer_tool
TOOL_EXECUTORS = {
    "get_customer_details": lambda args: _get_customer_details_impl(
        customer_number=int(args.get("customer_number")),
        account_suffix=int(args.get("account_suffix", 351)),
        branch_code=int(args.get("branch_code", 9142)),
    ),
    "get_card_summary_info": lambda args: _get_card_summary_info_impl(
        card_no=int(args.get("card_no"))
    ),
    "analyze_credit_offer": lambda args: analyze_credit_offer_tool(
        customer_number=int(args.get("customer_number")),
        card_no=int(args.get("card_no")),
        account_suffix=int(args.get("account_suffix", 351)),
        branch_code=int(args.get("branch_code", 9142)),
    ),
}


QWEN_CHAT_COMPLETIONS_URL = (
    "https://api-qwen-31-load-predictor-tmp-automation-test-3.apps.datascience.prod2.deniz.denizbank.com/v1/chat/completions"
)
QWEN_MODEL = "default"

HTTP_TIMEOUT = 60
QWEN_HEADERS = {
    "Content-Type": "application/json",
}

def qwen_chat_completions(payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.post(QWEN_CHAT_COMPLETIONS_URL, headers=QWEN_HEADERS, json=payload, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def _normalize_agno_message(m) -> Optional[Dict[str, Any]]:
    allowed = {"system", "user", "assistant", "tool"}
    if isinstance(m, dict):
        if m.get("role") not in allowed:
            return None
        d = {"role": m.get("role"), "content": m.get("content") or ""}
        for k in ("name", "tool_call_id", "tool_calls"):
            if k in m and m[k] is not None:
                d[k] = m[k]
        return d
    role = getattr(m, "role", None)
    if role not in allowed:
        return None
    d = {"role": role, "content": getattr(m, "content", "") or ""}
    for k in ("name", "tool_call_id", "tool_calls"):
        v = getattr(m, k, None)
        if v is not None:
            d[k] = v
    return d

class ModelResponseCompat:
    def __init__(self, content: str, raw: Optional[Dict[str, Any]] = None):
        self.content = content or ""
        self.raw = raw or {}
        self.tool_executions: List[Any] = []
    def __getattr__(self, name):
        return None

# Çoklu tool yürütücüleri
TOOL_EXECUTORS = {
    "get_customer_details": lambda args: _get_customer_details_impl(
        customer_number=int(args.get("customer_number")),
        account_suffix=int(args.get("account_suffix", 351)),
        branch_code=int(args.get("branch_code", 9142)),
    ),
    "get_card_summary_info": lambda args: _get_card_summary_info_impl(
        card_no=int(args.get("card_no"))
    ),
}

class CustomChatModel:
    name = "custom-qwen"
    id = "custom-qwen"
    provider = "custom"
    assistant_message_role = "assistant"
    user_message_role = "user"
    system_message_role = "system"
    tool_message_role = "tool"

    def get_instructions_for_model(self, tools): return ""
    def get_system_message_for_model(self, tools): return ""

    def _system_prompt(self) -> str:
        return """[ROLÜN]
Kullanıcının doğal dilde yazdığı isteği anla, gereken kimlik/parametreleri metinden çıkar, uygun tool’u (veya birden fazlasını) çağır, sonucu yorumla ve sade bir özet halinde sun.
Yanıt dili, kullanıcı hangi dilde yazdıysa odur (varsayılan Türkçe)."""

    def _run_single_tool_call(self, tc: Dict[str, Any]) -> Dict[str, Any]:
        fn = tc.get("function", {}) or {}
        fn_name = fn.get("name")
        raw_args = fn.get("arguments", "{}")
        call_id = tc.get("id")
        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
        except Exception:
            args = {}
        if fn_name not in TOOL_EXECUTORS:
            return {"role": "tool", "tool_call_id": call_id, "name": fn_name or "unknown",
                    "content": json.dumps({"error": f"Unsupported tool: {fn_name}"}, ensure_ascii=False)}
        try:
            result_obj = TOOL_EXECUTORS[fn_name](args)
            content = json.dumps(result_obj, ensure_ascii=False)
        except Exception as e:
            content = json.dumps({"error": str(e)}, ensure_ascii=False)
        return {"role": "tool", "tool_call_id": call_id, "name": fn_name, "content": content}

    def response(self, messages: List[Dict[str, Any]], tools=None, **kwargs) -> ModelResponseCompat:
        norm_messages = [nm for m in messages if (nm := _normalize_agno_message(m)) is not None]
        qwen_messages = [{"role": "system", "content": self._system_prompt()}, *norm_messages]
        first_req = {"model": QWEN_MODEL, "messages": qwen_messages, "tools": TOOL_SCHEMAS,
                     "tool_choice": "auto", "parallel_tool_calls": True, "temperature": 0.7, "max_tokens": 1024,"chat_template_kwargs":{"enable_thinking":False}}
        first_res = qwen_chat_completions(first_req)
        assistant_msg = first_res["choices"][0]["message"]
        tool_calls = assistant_msg.get("tool_calls") or []
        if not tool_calls:
            return ModelResponseCompat(content=assistant_msg.get("content", ""))
        tool_msgs = [self._run_single_tool_call(tc) for tc in tool_calls]
        followup_messages = [{"role": "system", "content": self._system_prompt()}, *norm_messages,
                             {"role": "assistant", "content": assistant_msg.get("content", ""), "tool_calls": tool_calls},
                             *tool_msgs]
        final_req = {"model": QWEN_MODEL, "messages": followup_messages,
                     "temperature": 0.7, "chat_template_kwargs": {"enable_thinking": False}}
        final_res = qwen_chat_completions(final_req)
        final_msg = final_res["choices"][0]["message"]
        return ModelResponseCompat(content=final_msg.get("content") or "", raw={"first": first_res, "final": final_res})

    def response_stream(self, messages: List[Dict[str, Any]], **kwargs) -> Iterable[Dict[str, str]]:
        r = self.response(messages, **kwargs)
        yield {"content": r.content}
