#!/usr/bin/env python3
"""Walkthrough script: parse -> filter -> score.

This script is intentionally verbose and deterministic:
- Uses `core.QueryParser` to parse a query.
- Uses `core.RecipeMatcher` (DB mode) to fetch top matches.
- Re-fetches full `Recipe` rows to evaluate hard filters and compute a score breakdown
  matching `RecipeMatcher._calculate_recipe_score`.

Run:
  python walkthroughs/search_case_01/run_case.py --query "..." --max-results 5

Requires:
  - DATABASE_URL set
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from core import QueryParser, RecipeMatcher, load_recipes  # noqa: E402


@dataclass(frozen=True)
class FilterEval:
    passed: bool
    reasons: List[str]


def _like_contains(haystack: str, needle: str) -> bool:
    return needle.lower() in (haystack or "").lower()


def evaluate_hard_filters(recipe, parsed: Dict[str, Any]) -> FilterEval:
    """Mirror the intent of DB-mode hard filtering in `RecipeMatcher._search_database`."""

    reasons: List[str] = []

    title_lower = (recipe.title or "").lower()
    search_text_lower = (recipe.search_text or "").lower()

    # 1) Excluded ingredients (instant reject)
    for exc in parsed.get("excluded_ingredients", []) or []:
        exc_lower = (exc or "").lower()
        if exc_lower and (exc_lower in title_lower or exc_lower in search_text_lower):
            reasons.append(f"REJECT: contains excluded ingredient '{exc_lower}'")
            return FilterEval(False, reasons)

    # 2) Nutrition constraints (instant reject if not met)
    nutrition_req: Dict[str, Dict[str, float]] = parsed.get("nutrition", {}) or {}
    for nutrient, constraints in nutrition_req.items():
        value = getattr(recipe, nutrient, None)
        if value is None:
            reasons.append(f"REJECT: missing nutrition field '{nutrient}'")
            return FilterEval(False, reasons)

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            reasons.append(f"REJECT: invalid nutrition value for '{nutrient}': {value!r}")
            return FilterEval(False, reasons)

        if "min" in constraints and numeric_value < float(constraints["min"]):
            reasons.append(f"REJECT: {nutrient} {numeric_value} < min {constraints['min']}")
            return FilterEval(False, reasons)
        if "max" in constraints and numeric_value > float(constraints["max"]):
            reasons.append(f"REJECT: {nutrient} {numeric_value} > max {constraints['max']}")
            return FilterEval(False, reasons)

    # 3) Required ingredients (must have ALL)
    for ing in parsed.get("ingredients", []) or []:
        ing_lower = (ing or "").lower()
        if ing_lower and (ing_lower not in title_lower and ing_lower not in search_text_lower):
            reasons.append(f"REJECT: missing required ingredient '{ing_lower}'")
            return FilterEval(False, reasons)

    # 4) Dish name (if specified)
    dish_name = parsed.get("dish_name")
    if dish_name:
        dish_lower = dish_name.lower()
        if dish_lower not in title_lower and dish_lower not in search_text_lower:
            reasons.append(f"REJECT: missing dish_name '{dish_lower}'")
            return FilterEval(False, reasons)

    reasons.append("PASS: all hard filters satisfied")
    return FilterEval(True, reasons)


def score_breakdown(recipe, parsed: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """Replicate `RecipeMatcher._calculate_recipe_score` but return detailed components."""

    score = 0.0
    breakdown: Dict[str, Any] = {
        "dish_name": {"points": 0.0, "details": None},
        "ingredients": [],
        "combo_bonus": {"points": 0.0, "details": None},
        "categories": {"points": 0.0, "matched": []},
        "meal_type": {"points": 0.0, "matched": False},
        "nutrition_bonus": {"points": 0.0, "constraints": list((parsed.get("nutrition") or {}).keys())},
    }

    title_lower = (recipe.title or "").lower()
    search_text_lower = (recipe.search_text or "").lower()

    # DISH NAME
    dish_name = parsed.get("dish_name")
    if dish_name:
        dish_lower = dish_name.lower()
        points = 0.0
        detail = {"dish": dish_lower, "rule": None}

        if title_lower == dish_lower:
            points = 100
            detail["rule"] = "exact title match"
        elif f" {dish_lower} " in f" {title_lower} ":
            title_words = title_lower.split()
            if dish_lower in title_words:
                position = title_words.index(dish_lower)
                if position == 0:
                    points = 60
                    detail["rule"] = "whole word in title (first word)"
                elif position == len(title_words) - 1:
                    points = 65
                    detail["rule"] = "whole word in title (last word)"
                else:
                    points = 55
                    detail["rule"] = "whole word in title (middle word)"
            else:
                points = 50
                detail["rule"] = "whole word-ish match"
        elif dish_lower in title_lower:
            points = 35
            detail["rule"] = "partial match in title"
        elif dish_lower in search_text_lower:
            points = 20
            detail["rule"] = "match in search_text"

        score += points
        breakdown["dish_name"]["points"] = points
        breakdown["dish_name"]["details"] = detail

    # REQUIRED INGREDIENTS
    required_ingredients = parsed.get("ingredients", []) or []
    for ingredient in required_ingredients:
        ing_lower = ingredient.lower()
        ing_points = 0.0
        detail: Dict[str, Any] = {
            "ingredient": ing_lower,
            "in_title": False,
            "in_search_text": False,
            "title_points": 0.0,
            "text_points": 0.0,
            "title_position_bonus": 0.0,
        }

        if ing_lower in title_lower:
            detail["in_title"] = True
            title_words = title_lower.split()
            base = 15
            pos_bonus = 0.0

            if ing_lower in title_words:
                position = title_words.index(ing_lower)
                if position == 0:
                    pos_bonus = 10
                elif position == 1:
                    pos_bonus = 8
                elif position == 2:
                    pos_bonus = 5
                else:
                    pos_bonus = 2
            else:
                pos_bonus = 5

            detail["title_position_bonus"] = pos_bonus
            detail["title_points"] = base + pos_bonus
            ing_points += detail["title_points"]

        if ing_lower in search_text_lower:
            detail["in_search_text"] = True
            detail["text_points"] = 10
            ing_points += 10

        score += ing_points
        breakdown["ingredients"].append({"points": ing_points, "details": detail})

    # COMBO BONUS
    if dish_name and required_ingredients:
        dish_lower = dish_name.lower()
        ingredients_in_title = sum(1 for ing in required_ingredients if ing.lower() in title_lower)
        if dish_lower in title_lower and ingredients_in_title > 0:
            points = 20.0
            proximity_awarded = False

            title_words = title_lower.split()
            if dish_lower in title_words:
                dish_idx = title_words.index(dish_lower)
                for ing in required_ingredients:
                    ing_lower = ing.lower()
                    if ing_lower in title_words:
                        ing_idx = title_words.index(ing_lower)
                        if abs(dish_idx - ing_idx) <= 2:
                            points += 10
                            proximity_awarded = True
                            break

            score += points
            breakdown["combo_bonus"]["points"] = points
            breakdown["combo_bonus"]["details"] = {
                "dish_in_title": True,
                "ingredients_in_title": ingredients_in_title,
                "proximity_bonus_awarded": proximity_awarded,
            }

    # CATEGORY
    categories = parsed.get("categories", []) or []
    matched_cats: List[str] = []
    for category in categories:
        cat_lower = category.lower()
        if cat_lower in search_text_lower:
            matched_cats.append(cat_lower)
            score += 12

    breakdown["categories"]["matched"] = matched_cats
    breakdown["categories"]["points"] = 12.0 * len(matched_cats)

    # MEAL TYPE
    meal_type = parsed.get("meal_type")
    if meal_type and meal_type.lower() in search_text_lower:
        score += 15
        breakdown["meal_type"]["points"] = 15.0
        breakdown["meal_type"]["matched"] = True

    # NUTRITION BONUS
    nutrition_req = parsed.get("nutrition", {}) or {}
    if nutrition_req:
        points = 20.0 * len(nutrition_req)
        score += points
        breakdown["nutrition_bonus"]["points"] = points

    breakdown["total_points"] = score
    breakdown["normalized_score"] = round(score / 100.0, 3)
    return score, breakdown


def _md_escape(text: Optional[str]) -> str:
    s = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    return s.replace("`", "\\`")


def render_report_md(payload: Dict[str, Any]) -> str:
    query = payload.get("query", "")
    parsed = payload.get("parsed", {}) or {}
    results = payload.get("results", []) or []

    lines: List[str] = []
    lines.append("# Search walkthrough report (case 01)")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("")
    lines.append("## Query")
    lines.append("")
    lines.append(f"- Raw: `{_md_escape(query)}`")
    if parsed.get("corrected_query"):
        lines.append(f"- Corrected: `{_md_escape(parsed.get('corrected_query'))}`")
    if parsed.get("spelling_corrections"):
        lines.append(f"- Corrections: `{_md_escape(json.dumps(parsed.get('spelling_corrections')))}`")
    lines.append("")

    lines.append("## Parsed output")
    lines.append("")
    lines.append(f"- dish_name: `{_md_escape(str(parsed.get('dish_name')))}`")
    lines.append(f"- ingredients (required): `{_md_escape(str(parsed.get('ingredients') or []))}`")
    lines.append(f"- excluded_ingredients: `{_md_escape(str(parsed.get('excluded_ingredients') or []))}`")
    lines.append(f"- categories: `{_md_escape(str(parsed.get('categories') or []))}`")
    lines.append(f"- meal_type: `{_md_escape(str(parsed.get('meal_type')))}`")
    lines.append(f"- nutrition: `{_md_escape(json.dumps(parsed.get('nutrition') or {}, sort_keys=True))}`")
    lines.append("")

    lines.append("## Hard filter order (DB mode)")
    lines.append("")
    lines.append("1. Excluded ingredients (instant reject)")
    lines.append("2. Nutrition constraints (instant reject)")
    lines.append("3. Required ingredients (ALL must be present)")
    lines.append("4. Dish name (if extracted)")
    lines.append("5. Score valid candidates")
    lines.append("")

    lines.append("## Results")
    lines.append("")
    if not results:
        lines.append("No results returned for this query.")
        lines.append("")
        return "\n".join(lines)

    for item in results:
        rank = item.get("rank")
        recipe_id = item.get("id")
        title = item.get("title")
        score_norm = item.get("score", {}).get("normalized_0_1")
        score_0_100 = item.get("score", {}).get("rule_score_0_100")
        hard_filters = item.get("hard_filters", {}) or {}
        breakdown = item.get("score", {}).get("breakdown", {}) or {}
        nutrition = item.get("nutrition", {}) or {}

        lines.append(f"### #{rank} — id={recipe_id} — score={score_norm} ({score_0_100}/100)")
        lines.append("")
        lines.append(f"Title: `{_md_escape(title)}`")
        lines.append("")

        lines.append("**Hard filters**")
        lines.append("")
        lines.append(f"- Passed: `{hard_filters.get('passed')}`")
        for reason in hard_filters.get("reasons", []) or []:
            lines.append(f"- { _md_escape(reason) }")
        lines.append("")

        lines.append("**Score breakdown**")
        lines.append("")
        lines.append(f"- dish_name: `{breakdown.get('dish_name', {}).get('points', 0)}`")

        ing_items = breakdown.get("ingredients", []) or []
        ing_total = sum((x.get("points") or 0) for x in ing_items)
        lines.append(f"- ingredients total: `{ing_total}`")
        for ing in ing_items:
            d = (ing.get("details") or {})
            lines.append(
                f"- ingredient `{_md_escape(d.get('ingredient'))}`: +`{ing.get('points')}` "
                f"(title=`{d.get('title_points')}`, text=`{d.get('text_points')}`)"
            )

        lines.append(f"- combo_bonus: `{breakdown.get('combo_bonus', {}).get('points', 0)}`")
        lines.append(f"- categories: `{breakdown.get('categories', {}).get('points', 0)}`")
        lines.append(f"- meal_type: `{breakdown.get('meal_type', {}).get('points', 0)}`")
        lines.append(f"- nutrition_bonus: `{breakdown.get('nutrition_bonus', {}).get('points', 0)}`")
        lines.append(f"- total_points: `{breakdown.get('total_points')}`")
        lines.append("")

        lines.append("**Nutrition (from DB)**")
        lines.append("")
        lines.append(f"- calories: `{nutrition.get('calories')}`")
        lines.append(f"- protein: `{nutrition.get('protein')}`")
        lines.append(f"- fat: `{nutrition.get('fat')}`")
        lines.append(f"- sodium: `{nutrition.get('sodium')}`")
        lines.append(f"- sugar: `{nutrition.get('sugar')}`")
        lines.append(f"- saturates: `{nutrition.get('saturates')}`")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Recipe Buddy search walkthrough (case 01)")
    parser.add_argument(
        "--query",
        default="high protein chicken include tomato no onion",
        help="Query to parse and run through the DB pipeline",
    )
    parser.add_argument("--max-results", type=int, default=5)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON (parsed query + per-result breakdown)",
    )
    parser.add_argument(
        "--write-json",
        default=None,
        help="Write machine-readable JSON to a file path (e.g., walkthroughs/search_case_01/output.json)",
    )
    parser.add_argument(
        "--report-path",
        default=None,
        help="Write a Markdown report to this path (e.g., walkthroughs/search_case_01/REPORT.md)",
    )

    args = parser.parse_args()

    if not os.environ.get("DATABASE_URL"):
        print("ERROR: DATABASE_URL is not set; DB-mode walkthrough requires it.")
        return 2

    recipes, metadata = load_recipes()
    qp = QueryParser()
    matcher = RecipeMatcher(recipes, metadata)

    parsed = qp.parse(args.query)

    # Run search
    results = matcher.search(parsed, max_results=args.max_results)

    # Re-fetch full rows for accurate filter + score breakdown
    from core.models import get_session, Recipe  # local import to honor DATABASE_URL

    session = get_session()
    try:
        enriched: List[Dict[str, Any]] = []
        for rank, r in enumerate(results, start=1):
            recipe_id = r.get("id")
            full = session.query(Recipe).filter(Recipe.id == recipe_id).first()
            if not full:
                continue

            filt = evaluate_hard_filters(full, parsed)
            total_score, breakdown = score_breakdown(full, parsed)

            enriched.append(
                {
                    "rank": rank,
                    "id": full.id,
                    "title": full.title,
                    "desc": full.description,
                    "hard_filters": {"passed": filt.passed, "reasons": filt.reasons},
                    "score": {
                        "rule_score_0_100": total_score,
                        "normalized_0_1": breakdown["normalized_score"],
                        "breakdown": breakdown,
                    },
                    "nutrition": {
                        "calories": full.calories,
                        "protein": full.protein,
                        "fat": full.fat,
                        "sodium": full.sodium,
                        "sugar": full.sugar,
                        "saturates": full.saturates,
                    },
                }
            )

        payload = {
            "query": args.query,
            "parsed": parsed,
            "results": enriched,
            "note": "Scoring breakdown mirrors core/recipe_matcher.py::_calculate_recipe_score",
        }

        if args.write_json:
            os.makedirs(os.path.dirname(os.path.abspath(args.write_json)), exist_ok=True)
            with open(args.write_json, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)

        if args.report_path:
            os.makedirs(os.path.dirname(os.path.abspath(args.report_path)), exist_ok=True)
            with open(args.report_path, "w", encoding="utf-8") as f:
                f.write(render_report_md(payload))

        if args.json:
            print(json.dumps(payload, indent=2, default=str))
            return 0

        # Human-readable output
        print("=" * 80)
        print("SEARCH WALKTHROUGH (CASE 01)")
        print("=" * 80)
        print(f"Query: {args.query}")
        print("\nParsed query:")
        print(f"  dish_name: {parsed.get('dish_name')}")
        print(f"  ingredients: {parsed.get('ingredients')}")
        print(f"  excluded_ingredients: {parsed.get('excluded_ingredients')}")
        print(f"  categories: {parsed.get('categories')}")
        print(f"  meal_type: {parsed.get('meal_type')}")
        print(f"  nutrition: {parsed.get('nutrition')}")

        print("\nTop results:")
        for item in enriched:
            print("-" * 80)
            print(f"#{item['rank']}  id={item['id']}  score={item['score']['normalized_0_1']}")
            print(f"Title: {item['title']}")

            hf = item["hard_filters"]
            print(f"Hard filters: {'PASS' if hf['passed'] else 'FAIL'}")
            for reason in hf["reasons"]:
                print(f"  - {reason}")

            b = item["score"]["breakdown"]
            print("Score breakdown (rule_score 0..100):")
            if b["dish_name"]["points"]:
                print(f"  - dish_name: +{b['dish_name']['points']} ({b['dish_name']['details']['rule']})")

            if b["ingredients"]:
                ing_total = sum(x["points"] for x in b["ingredients"])
                print(f"  - ingredients total: +{ing_total}")
                for ing in b["ingredients"]:
                    d = ing["details"]
                    print(
                        f"    - {d['ingredient']}: +{ing['points']} "
                        f"(title={d['title_points']}, text={d['text_points']})"
                    )

            if b["combo_bonus"]["points"]:
                print(f"  - combo_bonus: +{b['combo_bonus']['points']}")

            if b["categories"]["points"]:
                print(f"  - categories: +{b['categories']['points']} (matched={b['categories']['matched']})")

            if b["meal_type"]["points"]:
                print(f"  - meal_type: +{b['meal_type']['points']}")

            if b["nutrition_bonus"]["points"]:
                print(
                    f"  - nutrition_bonus: +{b['nutrition_bonus']['points']} "
                    f"(constraints={b['nutrition_bonus']['constraints']})"
                )

            print(f"TOTAL: {b['total_points']}  (normalized={b['normalized_score']})")

        print("=" * 80)
        return 0

    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
