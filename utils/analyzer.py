import json
import os


SKILLS_FILE = "skills.json"


def load_roles():
    if not os.path.exists(SKILLS_FILE):
        raise FileNotFoundError("skills.json file not found in folder!")

    with open(SKILLS_FILE, "r") as file:
        return json.load(file)


def analyze_text(text, job_roles):
    normalized_text = text.lower()
    results = []
    best_role = ""
    best_score = 0
    all_found_skills = set()

    for role, skills in job_roles.items():
        found = [skill for skill in skills if skill.lower() in normalized_text]
        missing = sorted(set(skills) - set(found))
        score = int((len(found) / len(skills)) * 100) if skills else 0

        if score > best_score:
            best_score = score
            best_role = role

        all_found_skills.update(found)
        results.append(
            {
                "role": role,
                "score": score,
                "found": found,
                "missing": missing,
            }
        )

    return {
        "results": results,
        "best_role": best_role,
        "best_score": best_score,
        "all_found_skills": sorted(all_found_skills),
    }


def get_score_color(score):
    if score >= 75:
        return "#16a34a"
    if score >= 45:
        return "#f59e0b"
    return "#dc2626"
