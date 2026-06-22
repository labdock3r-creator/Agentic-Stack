"""
MultiModelEvaluator v8 — Zaawansowany LLM-as-a-Judge

Funkcje:
- Prawdziwy LLM Judge
- Wsparcie dla dowolnej liczby modeli
- Scoring według kryteriów (bezpieczeństwo, kreatywność, dokładność itp.)
- Integracja z Hindsight (zapisywanie decyzji)
"""

from typing import List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from ..memory.hindsight_integration import HindsightMemory


class EvaluationResult(BaseModel):
    best_model: str = Field(description="Nazwa modelu, który dał najlepszą odpowiedź")
    best_response: str = Field(description="Najlepsza odpowiedź")
    scores: Dict[str, float] = Field(description="Oceny dla każdego modelu")
    reasoning: str = Field(description="Uzasadnienie wyboru")
    criteria_scores: Dict[str, Dict[str, float]] = Field(
        description="Szczegółowe oceny według kryteriów dla każdego modelu"
    )


class MultiModelEvaluator:
    def __init__(
        self,
        models: List,
        judge_model=None,
        criteria: Optional[List[str]] = None,
        hindsight: Optional[HindsightMemory] = None
    ):
        self.models = models
        self.judge_model = judge_model or models[0]  # domyślnie pierwszy model jako judge
        self.criteria = criteria or ["accuracy", "helpfulness", "safety", "clarity", "creativity"]
        self.hindsight = hindsight

        self.parser = JsonOutputParser(pydantic_object=EvaluationResult)

        self.evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Jesteś surowym, obiektywnym sędzią (LLM Judge). "
             "Oceń odpowiedzi kilku modeli według podanych kryteriów. "
             "Zwróć wynik wyłącznie w formacie JSON zgodnym ze schematem."),
            ("human",
             "Pytanie: {prompt}\n\n"
             "Odpowiedzi:\n{responses}\n\n"
             "Kryteria oceny: {criteria}\n\n"
             "Oceń każdą odpowiedź w skali 0-10 dla każdego kryterium. "
             "Wybierz najlepszą odpowiedź i podaj uzasadnienie.")
        ])

    def evaluate_responses(self, prompt: str, responses: List[str]) -> Dict:
        if len(responses) != len(self.models):
            raise ValueError("Liczba odpowiedzi musi być równa liczbie modeli")

        # Budujemy prompt z odpowiedziami
        responses_text = ""
        for i, (model, resp) in enumerate(zip(self.models, responses)):
            model_name = getattr(model, 'model_name', model.__class__.__name__)
            responses_text += f"\n--- Model {i+1} ({model_name}) ---\n{resp}\n"

        chain = self.evaluation_prompt | self.judge_model | self.parser

        result: EvaluationResult = chain.invoke({
            "prompt": prompt,
            "responses": responses_text,
            "criteria": ", ".join(self.criteria)
        })

        # Zapis do Hindsight
        if self.hindsight:
            self.hindsight.reflect_and_store(
                task_id=f"eval-{hash(prompt) % 100000}",
                reflection=f"Wybrano model {result.best_model}. Uzasadnienie: {result.reasoning}",
                phase="multi_model_evaluation"
            )

        return result.model_dump()

    def get_best_response(self, prompt: str, responses: List[str]) -> str:
        result = self.evaluate_responses(prompt, responses)
        return result["best_response"]