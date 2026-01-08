def print_assessment_pretty(result: dict) -> None:
    print("\n" + "=" * 80)
    print("ASSESSMENT OUTPUT")
    print("=" * 80)

    metadata = result.get("metadata", {})
    print(f"Assessment ID : {result.get('assessment_id')}")
    print(f"Course ID     : {result.get('course_id')}")
    print(f"Module ID     : {result.get('module_id')}")
    print(f"Total Questions: {metadata.get('total_questions')}")
    print("-" * 80)

    for idx, q in enumerate(result.get("questions", []), start=1):
        print(f"\nQuestion {idx}")
        print("-" * 40)
        print(q["question"])

        for opt in q["options"]:
            print(f"  {opt}")

        print(f"\nCorrect Answer: {q['correct_answer']}")
        print(f"Explanation   : {q['explanation']}")

        print("\n" + "-" * 80)

    print("\nEND OF ASSESSMENT")
    print("=" * 80 + "\n")
