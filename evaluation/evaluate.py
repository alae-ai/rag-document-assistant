
import json
import time
from pathlib import Path

from app.rag.rag_pipeline import RAGPipeline
from app.utils.logger import get_logger


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATASET_FILE = BASE_DIR / "dataset.json"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_FILE = RESULTS_DIR / "evaluation_results.json"

logger = get_logger(__name__)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

def load_dataset():
    """
    Load the evaluation dataset from JSON.

    Returns:
        list[dict]: Evaluation test cases.
    """

    if not DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {DATASET_FILE}"
        )

    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# Source evaluation
# --------------------------------------------------

def evaluate_sources(expected_sources, retrieved_chunks):
    """
    Check whether the expected documents were retrieved.

    Args:
        expected_sources (list[str]):
            Expected document names.

        retrieved_chunks (list):
            Chunks returned by the RAG pipeline.

    Returns:
        dict: Source evaluation metrics.
    """

    retrieved_sources = []

    for chunk in retrieved_chunks:
        payload = chunk.payload

        source = payload.get("source")

        if source and source not in retrieved_sources:
            retrieved_sources.append(source)

    expected_found = [
        source
        for source in expected_sources
        if source in retrieved_sources
    ]

    missing_sources = [
        source
        for source in expected_sources
        if source not in retrieved_sources
    ]

    source_recall = (
        len(expected_found) / len(expected_sources)
        if expected_sources
        else 1.0
    )

    return {
        "expected_sources": expected_sources,
        "retrieved_sources": retrieved_sources,
        "expected_sources_found": expected_found,
        "missing_sources": missing_sources,
        "source_recall": source_recall,
    }


# --------------------------------------------------
# Evaluate one question
# --------------------------------------------------

def evaluate_question(pipeline, test_case):
    """
    Evaluate one question through the complete RAG pipeline.

    Args:
        pipeline (RAGPipeline): RAG pipeline instance.
        test_case (dict): Evaluation test case.

    Returns:
        dict: Evaluation result.
    """

    question = test_case["question"]

    logger.info(
        "Evaluating question %s: %s",
        test_case["id"],
        question,
    )

    start_time = time.perf_counter()

    try:
        answer, chunks = pipeline.ask(question)

        elapsed_time = time.perf_counter() - start_time

        source_results = evaluate_sources(
            test_case.get("expected_sources", []),
            chunks,
        )

        result = {
            "id": test_case["id"],
            "question": question,
            "category": test_case.get("category"),
            "expected_intent": test_case.get("expected_intent"),

            "expected_answer": test_case["expected_answer"],
            "actual_answer": answer,

            "response_time_seconds": round(
                elapsed_time,
                4,
            ),

            "retrieved_chunks": len(chunks),

            "retrieved_results": [
                {
                    "source": chunk.payload.get(
                        "source",
                        "Unknown source",
                    ),
                    "chunk_id": chunk.payload.get(
                        "chunk_id"
                    ),
                    "score": getattr(
                        chunk,
                        "score",
                        None,
                    ),
                    "text": chunk.payload.get(
                        "text",
                        "",
                    ),
                }
                for chunk in chunks
            ],

            **source_results,

            "status": "success",
            "error": None,
        }

        logger.info(
            "Question %s evaluated successfully.",
            test_case["id"],
        )

        return result

    except Exception as exc:

        elapsed_time = time.perf_counter() - start_time

        logger.exception(
            "Evaluation failed for question %s.",
            test_case["id"],
        )

        return {
            "id": test_case["id"],
            "question": question,
            "category": test_case.get("category"),
            "expected_intent": test_case.get("expected_intent"),

            "expected_answer": test_case.get(
                "expected_answer"
            ),
            "actual_answer": None,

            "response_time_seconds": round(
                elapsed_time,
                4,
            ),

            "retrieved_chunks": 0,
            "retrieved_results": [],

            "expected_sources": test_case.get(
                "expected_sources",
                [],
            ),
            "retrieved_sources": [],
            "expected_sources_found": [],
            "missing_sources": test_case.get(
                "expected_sources",
                [],
            ),
            "source_recall": 0.0,

            "status": "failed",
            "error": str(exc),
        }


# --------------------------------------------------
# Summary
# --------------------------------------------------

def generate_summary(results):
    """
    Generate global evaluation statistics.

    Args:
        results (list[dict]): Evaluation results.

    Returns:
        dict: Evaluation summary.
    """

    total = len(results)

    successful = [
        result
        for result in results
        if result["status"] == "success"
    ]

    failed = [
        result
        for result in results
        if result["status"] == "failed"
    ]

    response_times = [
        result["response_time_seconds"]
        for result in successful
    ]

    source_recalls = [
        result["source_recall"]
        for result in successful
    ]

    average_response_time = (
        sum(response_times) / len(response_times)
        if response_times
        else 0
    )

    average_source_recall = (
        sum(source_recalls) / len(source_recalls)
        if source_recalls
        else 0
    )

    return {
        "total_questions": total,
        "successful_questions": len(successful),
        "failed_questions": len(failed),
        "success_rate": (
            len(successful) / total
            if total
            else 0
        ),
        "average_response_time_seconds": round(
            average_response_time,
            4,
        ),
        "average_source_recall": round(
            average_source_recall,
            4,
        ),
    }


# --------------------------------------------------
# Main evaluation
# --------------------------------------------------

def main():

    print("=" * 80)
    print("RAG SYSTEM EVALUATION")
    print("=" * 80)

    dataset = load_dataset()

    print(
        f"\nLoaded {len(dataset)} evaluation questions."
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pipeline = RAGPipeline()

    results = []

    for index, test_case in enumerate(
        dataset,
        start=1,
    ):

        print(
            f"\n[{index}/{len(dataset)}] "
            f"{test_case['question']}"
        )

        result = evaluate_question(
            pipeline,
            test_case,
        )

        results.append(result)

        if result["status"] == "success":

            print(
                f"  ✓ Completed in "
                f"{result['response_time_seconds']}s"
            )

            print(
                f"  Chunks retrieved: "
                f"{result['retrieved_chunks']}"
            )

            print(
                f"  Source recall: "
                f"{result['source_recall']:.2f}"
            )

        else:

            print(
                f"  ✗ Failed: "
                f"{result['error']}"
            )

    summary = generate_summary(results)

    evaluation = {
        "summary": summary,
        "results": results,
    }

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            evaluation,
            file,
            indent=4,
            ensure_ascii=False,
        )

    # --------------------------------------------------
    # Print summary
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)

    print(
        f"Total questions       : "
        f"{summary['total_questions']}"
    )

    print(
        f"Successful            : "
        f"{summary['successful_questions']}"
    )

    print(
        f"Failed                : "
        f"{summary['failed_questions']}"
    )

    print(
        f"Success rate          : "
        f"{summary['success_rate']:.2%}"
    )

    print(
        f"Average response time : "
        f"{summary['average_response_time_seconds']:.4f}s"
    )

    print(
        f"Average source recall : "
        f"{summary['average_source_recall']:.2%}"
    )

    print(
        f"\nResults saved to: "
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()

