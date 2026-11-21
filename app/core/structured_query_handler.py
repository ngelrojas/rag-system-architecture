# app/core/structured_query_handler.py — NLQ: natural language to SQL (5.5)
#
# A second query handler, beside AnswerQuestionHandler. It depends on two
# ports — LLMPort to write and phrase, StructuredQueryPort to run — and
# knows nothing about which database or model sits behind them.
# Nothing here stops a destructive query; that gap is closed in 6.3, at
# the port boundary, where compliance belongs.
import re

from app.core.structured_queries import StructuredAnswer, StructuredQuery
from app.ports import LLMPort, StructuredQueryPort

_FENCE = re.compile(r"^```(?:sql)?\s*|\s*```$", re.IGNORECASE)


def extract_sql(text: str) -> str:
    return _FENCE.sub("", text.strip()).strip().rstrip(";")


class StructuredQueryHandler:
    def __init__(self, llm: LLMPort, db: StructuredQueryPort, schema: str) -> None:
        self._llm = llm
        self._db = db
        self._schema = schema

    def handle(self, query: StructuredQuery) -> StructuredAnswer:
        sql = extract_sql(
            self._llm.complete(
                "You write one SQL SELECT statement for this database schema:\n"
                f"{self._schema}\n\nQuestion: {query.question}\nReturn only the SQL."
            )
        )
        rows = self._db.execute(sql)
        answer = self._llm.complete(
            f"Question: {query.question}\nRows returned by the database: {rows}\n"
            "Answer in one sentence using only these rows."
        )
        return StructuredAnswer(answer=answer, sql=sql, rows=rows)
