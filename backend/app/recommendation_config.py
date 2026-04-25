# Purpose: Define normalized curriculum, preference, and recommendation metadata for Apti backend services.
# Callers: schemas, ML service, API routes.
# Deps: None.
# API: Exported track/interest/preference constants and major metadata.
# Side effects: None.

from __future__ import annotations

MODEL_VERSION = "apti_v2"
FEATURE_VERSION = "apti_features_v2"
DATASET_VERSION = "apti_dataset_v2"
APP_IDENTIFIER = "apti"

VALID_RELIGION_RELATED_MAJOR_PREFERENCES = {
    "Not relevant",
    "Open to religious studies",
    "Islamic studies / education",
    "Christian theology / education",
    "Catholic theology / education",
    "Hindu studies",
    "Buddhist studies",
    "Other / unsure",
}

RELIGION_RELATED_MAJORS = {
    "Islamic Education",
    "Islamic Studies",
    "Theology",
    "Christian Religious Education",
    "Catholic Religious Education",
    "Religious Studies",
}

VALID_SMA_TRACKS = {"IPA", "IPS", "Bahasa", "Merdeka"}
VALID_INTERESTS = {
    "Technology",
    "Engineering",
    "Health",
    "Business",
    "Social",
    "Law",
    "Education",
    "Psychology",
    "Media",
    "Design",
    "Language",
    "Environment",
    "Data / AI",
}
VALID_PREFERENCE_VALUES = {
    "Numbers",
    "People",
    "Creativity",
    "Technical",
    "Social",
    "Teamwork",
    "Independent",
}

TRACK_SUBJECT_RULES = {
    "IPA": {
        "required": {"religion", "civics", "indonesian", "english", "general_math", "pjok", "arts", "biology", "physics", "chemistry", "advanced_math"},
        "optional": {"informatics"},
        "elective_range": (0, 0),
    },
    "IPS": {
        "required": {"religion", "civics", "indonesian", "english", "general_math", "pjok", "arts", "sociology", "geography", "economics", "history"},
        "optional": {"informatics"},
        "elective_range": (0, 0),
    },
    "Bahasa": {
        "required": {"religion", "civics", "basic_math", "history", "indonesian_literature", "english_literature", "anthropology"},
        "optional": {"foreign_language_arabic", "foreign_language_japanese", "foreign_language_german", "foreign_language_mandarin", "foreign_language_french", "foreign_literature"},
        "elective_range": (0, 0),
    },
    "Merdeka": {
        "required": {"religion", "pancasila", "indonesian", "math", "english", "pjok", "arts"},
        "optional": {"informatics"},
        "elective_range": (4, 5),
        "electives": {"biology", "chemistry", "physics", "advanced_math", "sociology", "economics", "geography", "anthropology", "advanced_language", "foreign_language", "entrepreneurship", "informatics"},
    },
}

MAJOR_METADATA = {
    "Computer Science": {
        "cluster": "STEM",
        "careers": ["Software Engineer", "AI Engineer", "Product Analyst"],
        "strengths": ["Logic-heavy problem solving", "Systems thinking", "Build orientation"],
        "tradeoffs": ["Requires sustained technical depth", "Needs comfort with iteration"],
        "alternatives": ["Information Systems", "Mathematics"],
    },
    "Information Systems": {
        "cluster": "STEM",
        "careers": ["Business Analyst", "Systems Consultant", "Product Operations"],
        "strengths": ["Technology + business bridge", "Process design", "Decision support"],
        "tradeoffs": ["Less purely technical than computer science"],
        "alternatives": ["Computer Science", "Management"],
    },
    "Civil Engineering": {
        "cluster": "STEM",
        "careers": ["Project Engineer", "Infrastructure Planner", "Site Engineer"],
        "strengths": ["Applied physics", "Structured planning", "Long-horizon thinking"],
        "tradeoffs": ["Field-work heavy in many roles"],
        "alternatives": ["Electrical Engineering", "Architecture"],
    },
    "Electrical Engineering": {
        "cluster": "STEM",
        "careers": ["Controls Engineer", "Power Systems Engineer", "Embedded Engineer"],
        "strengths": ["Technical depth", "Precision", "Applied mathematics"],
        "tradeoffs": ["Steep quantitative curve"],
        "alternatives": ["Computer Science", "Civil Engineering"],
    },
    "Medicine": {
        "cluster": "Health",
        "careers": ["Doctor", "Clinical Researcher", "Healthcare Leader"],
        "strengths": ["Biology-led mastery", "Patient impact", "Long-term commitment"],
        "tradeoffs": ["Long education path", "High emotional load"],
        "alternatives": ["Pharmacy", "Biology"],
    },
    "Pharmacy": {
        "cluster": "Health",
        "careers": ["Pharmacist", "Drug Safety Specialist", "Clinical Support"],
        "strengths": ["Chemistry precision", "Health systems relevance", "Regulatory awareness"],
        "tradeoffs": ["Detail-heavy study load"],
        "alternatives": ["Medicine", "Biology"],
    },
    "Biology": {
        "cluster": "Health",
        "careers": ["Research Assistant", "Lab Analyst", "Environmental Scientist"],
        "strengths": ["Scientific observation", "Health and environment overlap"],
        "tradeoffs": ["Career path often needs specialization"],
        "alternatives": ["Medicine", "Psychology"],
    },
    "Mathematics": {
        "cluster": "STEM",
        "careers": ["Quant Analyst", "Data Scientist", "Actuarial Analyst"],
        "strengths": ["Abstract reasoning", "Pattern detection", "High transferability"],
        "tradeoffs": ["Theory can feel demanding"],
        "alternatives": ["Computer Science", "Accounting"],
    },
    "Psychology": {
        "cluster": "Social",
        "careers": ["Counselor", "HR Specialist", "Behavior Researcher"],
        "strengths": ["People insight", "Listening", "Behavior analysis"],
        "tradeoffs": ["Needs strong empathy + patience"],
        "alternatives": ["Communication Studies", "Education"],
    },
    "Communication Studies": {
        "cluster": "Social",
        "careers": ["Strategist", "PR Specialist", "Content Lead"],
        "strengths": ["Narrative clarity", "Audience awareness", "Media fluency"],
        "tradeoffs": ["Portfolio and execution matter a lot"],
        "alternatives": ["Law", "Visual Communication Design"],
    },
    "Law": {
        "cluster": "Social",
        "careers": ["Lawyer", "Policy Analyst", "Compliance Officer"],
        "strengths": ["Argument quality", "Reading stamina", "Public reasoning"],
        "tradeoffs": ["Text-heavy and competitive"],
        "alternatives": ["Communication Studies", "Psychology"],
    },
    "English Education": {
        "cluster": "Social",
        "careers": ["Teacher", "Curriculum Developer", "Language Trainer"],
        "strengths": ["Language fluency", "Guiding others", "Structured communication"],
        "tradeoffs": ["Strong fit if teaching energy is real"],
        "alternatives": ["Communication Studies", "Psychology"],
    },
    "Management": {
        "cluster": "Business",
        "careers": ["Brand Associate", "Business Development", "Operations Lead"],
        "strengths": ["Business judgment", "Coordination", "Adaptability"],
        "tradeoffs": ["Needs self-direction to stand out"],
        "alternatives": ["Accounting", "Information Systems"],
    },
    "Accounting": {
        "cluster": "Business",
        "careers": ["Auditor", "Finance Analyst", "Tax Associate"],
        "strengths": ["Numerical consistency", "Detail discipline", "Business relevance"],
        "tradeoffs": ["Precision work can feel repetitive"],
        "alternatives": ["Management", "Mathematics"],
    },
    "Visual Communication Design": {
        "cluster": "Arts",
        "careers": ["Designer", "Art Director", "Brand Visual Strategist"],
        "strengths": ["Creative execution", "Visual communication", "Portfolio building"],
        "tradeoffs": ["Output quality and practice matter a lot"],
        "alternatives": ["Communication Studies", "Management"],
    },
}

MAJOR_CLUSTERS = {
    "STEM / Technology": [
        "Computer Science",
        "Informatics Engineering",
        "Information Systems",
        "Data Science",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Civil Engineering",
        "Industrial Engineering",
        "Architecture",
        "Cybersecurity",
    ],
    "Health / Natural Science": [
        "Medicine",
        "Nursing",
        "Pharmacy",
        "Nutrition",
        "Public Health",
        "Biology",
        "Chemistry",
        "Mathematics",
        "Statistics",
        "Environmental Science",
    ],
    "Business / Economy": [
        "Management",
        "Accounting",
        "Development Economics",
        "Digital Business",
        "Entrepreneurship",
        "Business Administration",
        "Finance",
    ],
    "Social / Humanities": [
        "Psychology",
        "Law",
        "Communication Science",
        "International Relations",
        "Sociology",
        "Political Science",
        "Public Administration",
    ],
    "Language / Culture": [
        "Indonesian Literature",
        "English Literature",
        "Japanese Literature",
        "French Literature",
        "Linguistics",
        "Anthropology",
        "Indonesian Language Education",
        "English Education",
        "Translation Studies",
    ],
    "Creative": [
        "Visual Communication Design",
        "Product Design",
        "Film and Television",
        "Fine Arts",
        "Music",
        "Animation",
        "Creative Media",
    ],
    "Education": [
        "Elementary Teacher Education",
        "Guidance and Counseling",
        "Educational Technology",
        "Mathematics Education",
        "Biology Education",
        "Economics Education",
        "Language Education",
    ],
    "Religion-related": sorted(RELIGION_RELATED_MAJORS),
}

MAJOR_CLUSTER_MAP = {major: cluster for cluster, majors in MAJOR_CLUSTERS.items() for major in majors}
