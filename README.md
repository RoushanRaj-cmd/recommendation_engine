AI-Powered Internship Recommendation Engine 🧠✨

It’s an empathetic, AI-powered recommendation engine designed to guide India's aspiring youth, especially first-generation learners, through the complexities of finding the right internship. Our mission is to bridge the opportunity gap by transforming an overwhelming search into a simple, personal, and encouraging conversation. Technically, it’s a multilingual, dissonance‑aware recommender that returns 3–5 explained internship matches using TF/IDF baseline, feasibility signals, and diversity re‑ranking .

This project is not for a hackathon; it is an ongoing effort to build a practical, scalable, and impactful solution to demystify the internship search process for those who need it most.
## Current Status

Our development is structured with separate frontend and backend folders to ensure clean, manageable code.

    ✅ Recommendation Engine: The core model is complete, generalized, and tested. It features a hybrid approach to skill matching, empathetic logic, and result diversity.

    ✅ Backend API: A robust and scalable API built with FastAPI is complete and ready for integration. It reads from a database and uses an external configuration for easy tuning.

    ⏳ Frontend Development: The user interface is designed and in development.

    ⏳ Full Integration: The final connection between the frontend and backend is the next major milestone.

## Core Features (Backend Complete)

    Hybrid Recommendation Core: Combines TF-IDF for technical skills with a custom-built tagger for soft/generic skills, ensuring no part of a user's profile is ignored.

    Empathetic "Stepping Stone" Logic: If no strong direct matches are found, the engine intelligently suggests foundational internships that help users build the necessary skills for their aspirational roles.

    Result Diversity (MMR): Implements Maximal Marginal Relevance to ensure the top recommendations are varied and not just slight variations of the same role.

    Explainable AI ("Why Cards"): The API returns simple, human-readable reasons for each match, building user trust and confidence.

    Generalized & Configurable: The system is decoupled from static data (using a database) and its logic is controlled by an external config.json file, making it highly adaptable.

## Technology Stack

    Backend: FastAPI, Python

    AI / ML: Scikit-learn, Pandas, NumPy

    Database: SQLite (for prototype), MongoDB (planned for production)

    Frontend (In Progress): HTML, CSS, JavaScript (as a Progressive Web App)

    Govt-native stack: Bhashini, MeghRaj cloud

    Other tools and softwares: Git, Figma, VS Code

## Getting Started (Backend)

To run the backend and the recommendation model locally:

    Take the files of “Backend” folder.

    Create a virtual environment and install dependencies:

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt


    Prepare the database:
    Run the loading script once to create and populate internships.db from your CSV.

    python load_data.py


    Run the server:

    fastapi dev server.py 

    The API will be available at http://127.0.0.1:8000.

## Testing the Model via API Call

You can test the live API using curl. The following command simulates a request from a user interested in a "Web Development" role in "Ranchi".

curl -X POST \
     -H "Content-Type: application/json" \
     -d '{
          "skills": "Web Development; Java",
          "sector": "IT/Software",
          "location": "Ranchi",
          "top_k": 3
     }' \
     [http://127.0.0.1:8000/api/recommend](http://127.0.0.1:8000/api/recommend)


Expected Response:

You will receive a JSON response with a "direct_match" type and a list of results, each containing human-readable "match_reasons".

{
    "recommendation_type": "direct_match",
    "suggestion_prompt": "Here are your top personalized recommendations!",
    "results": [
        {
            "id": 485,
            "sector": "IT/Software",
            "skills": "Web Development; Cybersecurity; Java",
            "education": "B.Tech Computer Science",
            "location": "Ranchi",
            "final_score": 0.812051984070451,
            "match_reasons": [
                "Good technical skill alignment.",
                "It's in your preferred sector: IT/Software.",
                "Located in your preferred city: Ranchi."
            ]
        }
    ]
}

You can view our partially completed website via this url - https://ayush-delta.github.io/Recommendation-System/internships.html
