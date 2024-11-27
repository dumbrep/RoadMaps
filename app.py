import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import initialize_agent, Tool
import os


#Load environment variables

open_token = st.secrets["OPENAI_KEY"]
os.environ["OPENAI_API_KEY"] = open_token

# Initialize model 
model = ChatOpenAI(model="gpt-3.5-turbo")

#Tools declarations
@tool
def generate_roadmap_tool(details: str) -> str:
    """Generates a study roadmap based on the student's details."""
    response = model.invoke(        
            f"""
                I am a JEE aspirant. Prepare a roadmap for my study based on my provided content.
                The roadmap should include:
                1. Subject-wise information: How much time should I spend daily on each subject.
                2. Focus area: Which subject should I focus on more.
                3. Revision and mock tests: Include time for revision and mock tests.
                4. Daily and weekly routines: Include daily and weekly routines.
                prepare pointwise roadmap were points are :
                    -Daily Time Allocation: Hours for Physics, Chemistry, and Math.
                    -Focus Areas: Strengthen weak topics and prioritize high-weightage chapters.
                    -Revision Schedule: Daily reviews and weekly topic recaps.
                    -Mock Tests: Weekly full-length and sectional tests with detailed analysis.
                    -Syllabus Completion: Milestones for covering the syllabus with a buffer period.
                    -Daily Routine: Active study in the morning, revision midday, practice in the evening.
                    -Breaks: Short breaks for better focus and energy retention.

                My current details are: {details}

                
            """
    )
    return response.content.strip()


@tool
def regenerate_roadmap_tool(changes: str) -> str:
    """Refines an existing roadmap based on feedback or suggestions."""
    response = model.invoke(
            f"""
            I am giving some changes to your old roadmap. Change it according to my suggestions.

            Old Roadmap: {st.session_state.roadmap}
            ----------------------------------------------------
            Changes: {changes}

            Do not include any formality lines or introduction by your side.
            Give the changed roadmap in the same format as the original roadmap.
            """
    )
    return response.content.strip()


tools = [
    Tool(name="GenerateRoadmap", func=generate_roadmap_tool, description="Generate roadmap based on given information"),
    Tool(name="RegenerateRoadmap", func=regenerate_roadmap_tool, description="Redesign the generated roadmap based on provided suggestions"),
]

agent = initialize_agent(llm=model, tools=tools, agent="zero-shot-react-description", handle_parsing_errors=True)

def regenerate(changes):
    updated_roadmap = agent.run(f"Refine this roadmap: {st.session_state.roadmap} with feedback: {changes}")
    st.session_state.roadmap = updated_roadmap  # Save the updated roadmap           
            
    st.success("Roadmap updated successfully!")
    st.write(st.session_state.roadmap)   

# Initialize session state
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None

if "final" not in st.session_state:
    st.session_state.final = False
if "editing" not in st.session_state:
    st.session_state.editing = False

# Sidebar for page navigation
page = st.sidebar.selectbox("Who are you?", ["Student", "Parent/Teacher"])

if page == "Student":
    st.title("Welcome dear aspirant ! 🎓")
    st.write("Please provide your details to generate a personalized roadmap.")

    # Input fields for student details
 
    months = st.sidebar.number_input("Months remaining for your examination", min_value=1, max_value=24, value=6)
    st.sidebar.write("Enter marks obtained in last test")
    physics_marks = st.sidebar.number_input("Physics Marks", min_value=0, max_value=100, value=80)
    chemistry_marks = st.sidebar.number_input("Chemistry Marks", min_value=0, max_value=100, value=70)
    math_marks = st.sidebar.number_input("Mathematics Marks", min_value=0, max_value=100, value=65)
    st.sidebar.write("How much syllabus you have coverd?")
    physics_per = st.sidebar.number_input("Physics Syllabus Completion (%)", min_value=0, max_value=100, value=69)
    chemistry_per = st.sidebar.number_input("Chemistry Syllabus Completion (%)", min_value=0, max_value=100, value=80)
    math_per = st.sidebar.number_input("Mathematics Syllabus Completion (%)", min_value=0, max_value=100, value=70)

    if st.session_state.roadmap:
        st.write(st.session_state.roadmap)
    else:
        if st.button("Generate Roadmap"):
            with st.spinner("Generating your personalized roadmap..."):
                try:
                    input_data = (
                        f"I have {months} months for preparation. My marks are: "
                        f"Physics = {physics_marks}, Chemistry = {chemistry_marks}, Mathematics = {math_marks}. "
                        f"My syllabus completion is: Physics = {physics_per}%, Chemistry = {chemistry_per}%, Mathematics = {math_per}%. "
                        f"Generate a roadmap accordingly."
                    )
                    result = agent.run(input_data)
                    st.session_state.roadmap = result
                    #Save roadmap in session state
                    st.success("Roadmap generated successfully!")
                    if result:
                        if st.session_state.final == True:
                            st.container(st.session_state.roadmap)
                        else:
                            st.write("Review of roadmap by parents/teachers is pending!")

                except Exception as e:
                    st.error(f"An error occurred: {e}")

elif page == "Parent/Teacher":
    st.title("Welcome to Reviewer section📚")
    st.subheader("Please review and give suggestions")

    if st.session_state.roadmap:
        
        st.write(st.session_state.roadmap)

        #Button to start making changes
        if st.button("Make changes"):
            st.session_state.editing = True  

        if st.session_state.get("editing", True):
            # Text area for suggestions
            changes = st.text_area("Suggest changes")

            # Button to regenerate the roadmap
            if st.button("Regenerate"):
                regenerate(changes)
                #Update the roadmap with new feedback
                
            # Button to finalize the roadmap
        if st.button("Finalize"):
            st.session_state.editing = False  
            st.session_state.final = True  
            st.success("Roadmap finalized!")
            st.write(st.session_state.roadmap)  
    else:
        st.warning("No roadmap has been generated yet. Please generate it on the Student page.")
