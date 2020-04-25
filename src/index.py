
import random

# --------------- Main handler ------------------

def lambda_handler(event, context):

    # Prevents other apps from making request to this function
    if (event['session']['application']['applicationId'] !=
             "amzn1.ask.skill.a995478c-936c-40b2-895c-fe0d4bb90ae9"):
         raise ValueError("Invalid Application ID")
    
    
    # Directs various requests
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                               event['session'])
    if event['request']['type'] == "LaunchRequest":
            return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
            return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
            return on_session_ended(event['request'], event['session'])
        

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ChooseTableIntent":
        return set_table_in_session(intent, session)
    elif intent_name == "AnswerQuestionIntent":
        return check_answer(intent, session)
    elif intent_name == "AMAZON.YesIntent":
        return get_question(session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request(session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


    
# --------------- Functions that control the skill's behavior ------------------
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Multiplication Table dojo! " \
                    "Please tell me which table you would like to practice by saying, " \
                    "I would like to practice multiplication by five"
                    
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me which table you would like to practice by saying, " \
                    "I would like to practice multiplication by five" 
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request(session):
    card_title = "Session Ended"
    speech_output = "Thank you for using the Multiplication Table helper! " \
                "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
    


    
def set_table_in_session(intent, session):
    """ Sets the kind of multiplication table in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    should_end_session = False
    try:
            int(intent['slots']['Number']['value'])
            which_table = intent['slots']['Number']['value']
            session_attributes = {"table": which_table, "questions_asked": 0, "score": 0}
            card_title = "Begin Training?"
            speech_output = "Okay! Ready to begin your training of ten multiplication questions?"
            reprompt_text = "Are you ready to begin your training?"
    except:
        if "score" in session.get('attributes', {}):
            session_attributes = {}
            card_title= "Reprompt"
            speech_output = "Are you ready to begin your training?"
            reprompt_text = "Are you ready to begin your training?"
        else:
            session_attributes = {}
            card_title= "Reprompt"
            speech_output = "I didn't quite catch that. " \
                                "You can tell me what table you'd like to practice by saying, " \
                                "I would like to practice multiplication by five."
            reprompt_text = "I didn't quite catch that. " \
                                "You can tell me what table you'd like to practice by saying, " \
                                "I would like to practice multiplication by five."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_question(session):
    should_end_session = False
    if "table" in session.get('attributes', {}):
        session_attributes = session['attributes']
        first_number = session['attributes']['table']
        second_number = random.randint(1,12)
        answer = int(first_number)*second_number
        
        card_title = "Dojo in Session"
        session_attributes.update({"answer": answer,
                                "questions_asked": session['attributes'].get('questions_asked') + 1
                                })
        speech_output = "What is " + str(first_number) + " times " + str(second_number) + "?"
        reprompt_text = None
    else:
        card_title = "Reprompt"
        speech_output = "I didn't quite catch that. " \
                        "You can tell me what table you'd like to practice by saying, " \
                        "I would like to practice multiplication by five."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def check_answer(intent, session):
    session_attributes = session['attributes']
    card_title = "Dojo in Session"
    reprompt_text = None
    should_end_session = False
    speech_output = ""
    if "answer" in session.get('attributes', {}):
        if 'Number' in intent['slots']:
            correct_answer = int(session['attributes']['answer'])
            try:
                user_response = int(intent['slots']['Number']['value'])
                if user_response == correct_answer:
                    session_attributes.update(add_score(session))
                    speech_output= "Correct!"
                else:
                    speech_output = "Incorrect! The correct answer was " + str(correct_answer) + "."
            except:
                speech_output = "Incorrect! The correct answer was " + str(correct_answer) + "."
        else:
            speech_output = "Incorrect! The correct answer was " + str(correct_answer) + "."
            
        if session['attributes']['questions_asked'] == 10:
            should_end_session = True
            speech_output = speech_output + " You answered " + str(session['attributes']['score']) \
                        + " questions correctly out of " + str(session['attributes']['questions_asked']) + \
                        " questions asked! Great job, and come back to train again soon! "
                        
        else:
            first_number = session['attributes']['table']
            second_number = random.randint(1,12)
            answer = int(first_number)*second_number
            
            session_attributes.update({"answer": answer,
                                    "questions_asked": session['attributes'].get('questions_asked') + 1
                                    })
            speech_output = speech_output + " What is " + str(first_number) + " times " + str(second_number) + "?"
    elif "score" in session.get('attributes', {}):
        card_title = "Reprompt"
        speech_output = "I didn't quite catch that. " \
                            "Would you like to start your training? Please answer by saying " \
                            "Yes or Stop"
    else:
        card_title = "Reprompt"
        speech_output = "I didn't quite catch that. " \
                        "You can tell me what table you'd like to practice by saying, " \
                        "I would like to practice multiplication by five."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def reset_score():
    return {"score": 0}
def add_score(session):
    return {"score": session['attributes'].get('score',0) + 1}


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


