from flask import Flask, render_template, request, jsonify
import random
import time
from nltk.chat.util import Chat, reflections
import re


reflections_care = {
    "i am": "you are",
    "i was": "you were",
    "i": "you",
    "i'm": "you are",
    "i'd": "you would",
    "i've": "you have",
    "i'll": "you will",
    "my": "your",
    "you are": "I am",
    "you were": "I was",
    "you've": "I have",
    "you'll": "I will",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "me": "you",
}
"""
"""
responses_ZC = (
    # Zen Chatbot opens with the line "Welcome, my child." The usual
    # response will be a greeting problem: 'good' matches "good morning",
    # "good day" etc, but also "good grief!"  and other sentences starting
    # with the word 'good' that may not be a greeting
    (
        r"(hello(.*))|(good [a-zA-Z]+)",
        (
            "The path to enlightenment is often difficult to see.",
            "Greetings. I sense your mind is troubled. Tell me of your troubles.",
            "Ask the question you have come to ask.",
            "Hello. Do you seek englightenment?",
        ),
    ),
    # "I need" and "I want" can be followed by a thing (eg 'help')
    # or an action (eg 'to see you')
    #
    # This is a problem with this style of response -
    # person:    "I need you"
    # chatbot:    "me can be achieved by hard work and dedication of the mind"
    # i.e. 'you' is not really a thing that can be mapped this way, so this
    # interpretation only makes sense for some inputs
    #
    (
        r"i need (.*)",
        (
            "%1 can be achieved by hard work and dedication of the mind.",
            "%1 is not a need, but a desire of the mind. Clear your mind of such concerns.",
            "Focus your mind on%1, and you will find what you need.",
        ),
    ),
    (
        r"i want (.*)",
        (
            "Desires of the heart will distract you from the path to enlightenment.",
            "Will%1 help you attain enlightenment?",
            "Is%1 a desire of the mind, or of the heart?",
        ),
    ),
    # why questions are separated into three types:
    # "why..I"     e.g. "why am I here?" "Why do I like cake?"
    # "why..you"    e.g. "why are you here?" "Why won't you tell me?"
    # "why..."    e.g. "Why is the sky blue?"
    # problems:
    #     person:  "Why can't you tell me?"
    #     chatbot: "Are you sure I tell you?"
    # - this style works for positives (e.g. "why do you like cake?")
    #   but does not work for negatives (e.g. "why don't you like cake?")
    (r"why (.*) i (.*)\?", ("You%1%2?", "Perhaps you only think you%1%2")),
    (r"why (.*) you(.*)\?", ("Why%1 you%2?", "%2 I%1", "Are you sure I%2?")),
    (r"why (.*)\?", ("I cannot tell you why%1.", "Why do you think %1?")),
    # e.g. "are you listening?", "are you a duck"
    (
        r"are you (.*)\?",
        ("Maybe%1, maybe not%1.", "Whether I am%1 or not is God's business."),
    ),
    # e.g. "am I a duck?", "am I going to die?"
    (
        r"am i (.*)\?",
        ("Perhaps%1, perhaps not%1.", "Whether you are%1 or not is not for me to say."),
    ),
    # what questions, e.g. "what time is it?"
    # problems:
    #     person:  "What do you want?"
    #    chatbot: "Seek truth, not what do me want."
    (r"what (.*)\?", ("Seek truth, not what%1.", "What%1 should not concern you.")),
    # how questions, e.g. "how do you do?"
    (
        r"how (.*)\?",
        (
            "How do you suppose?",
            "Will an answer to that really help in your search for enlightenment?",
            "Ask yourself not how, but why.",
        ),
    ),
    # can questions, e.g. "can you run?", "can you come over here please?"
    (
        r"can you (.*)\?",
        (
            "I probably can, but I may not.",
            "Maybe I can%1, and maybe I cannot.",
            "I can do all, and I can do nothing.",
        ),
    ),
    # can questions, e.g. "can I have some cake?", "can I know truth?"
    (
        r"can i (.*)\?",
        (
            "You can%1 if you believe you can%1, and have a pure spirit.",
            "Seek truth and you will know if you can%1.",
        ),
    ),
    # e.g. "It is raining" - implies the speaker is certain of a fact
    (
        r"it is (.*)",
        (
            "How can you be certain that%1, when you do not even know yourself?",
            "Whether it is%1 or not does not change the way the world is.",
        ),
    ),
    # e.g. "is there a doctor in the house?"
    (
        r"is there (.*)\?",
        ("There is%1 if you believe there is.", "It is possible that there is%1."),
    ),
    # e.g. "is it possible?", "is this true?"
    (r"is(.*)\?", ("%1 is not relevant.", "Does this matter?")),
    # non-specific question
    (
        r"(.*)\?",
        (
            "Do you think %1?",
            "You seek the truth. Does the truth seek you?",
            "If you intentionally pursue the answers to your questions, the answers become hard to see.",
            "The answer to your question cannot be told. It must be experienced.",
        ),
    ),
    # expression of hate of form "I hate you" or "Kelly hates cheese"
    (
        r"(.*) (hate[s]?)|(dislike[s]?)|(don\'t like)(.*)",
        (
            "Perhaps it is not about hating %2, but about hate from within.",
            "Weeds only grow when we dislike them",
            "Hate is a very strong emotion.",
        ),
    ),
    # statement containing the word 'truth'
    (
        r"(.*) truth(.*)",
        (
            "Seek truth, and truth will seek you.",
            "Remember, it is not the spoon which bends - only yourself.",
            "The search for truth is a long journey.",
        ),
    ),
    # desire to do an action
    # e.g. "I want to go shopping"
    (
        r"i want to (.*)",
        ("You may %1 if your heart truly desires to.", "You may have to %1."),
    ),
    # desire for an object
    # e.g. "I want a pony"
    (
        r"i want (.*)",
        (
            "Does your heart truly desire %1?",
            "Is this a desire of the heart, or of the mind?",
        ),
    ),
    # e.g. "I can't wait" or "I can't do this"
    (
        r"i can\'t (.*)",
        (
            "What we can and can't do is a limitation of the mind.",
            "There are limitations of the body, and limitations of the mind.",
            "Have you tried to%1 with a clear mind?",
        ),
    ),
    # "I think.." indicates uncertainty. e.g. "I think so."
    # problem: exceptions...
    # e.g. "I think, therefore I am"
    (
        r"i think (.*)",
        (
            "Uncertainty in an uncertain world.",
            "Indeed, how can we be certain of anything in such uncertain times.",
            "Are you not, in fact, certain that%1?",
        ),
    ),
    # "I feel...emotions/sick/light-headed..."
    (
        r"i feel (.*)",
        (
            "Your body and your emotions are both symptoms of your mind."
            "What do you believe is the root of such feelings?",
            "Feeling%1 can be a sign of your state-of-mind.",
        ),
    ),
    # exclaimation mark indicating emotion
    # e.g. "Wow!" or "No!"
    (
        r"(.*)!",
        (
            "I sense that you are feeling emotional today.",
            "You need to calm your emotions.",
        ),
    ),
    # because [statement]
    # e.g. "because I said so"
    (
        r"because (.*)",
        (
            "Does knowning the reasons behind things help you to understand"
            " the things themselves?",
            "If%1, what else must be true?",
        ),
    ),
    # yes or no - raise an issue of certainty/correctness
    (
        r"(yes)|(no)",
        (
            "Is there certainty in an uncertain world?",
            "It is better to be right than to be certain.",
        ),
    ),
    # sentence containing word 'love'
    (
        r"(.*)love(.*)",
        (
            "Think of the trees: they let the birds perch and fly with no intention to call them when they come, and no longing for their return when they fly away. Let your heart be like the trees.",
            "Free love!",
        ),
    ),
    # sentence containing word 'understand' - r
    (
        r"(.*)understand(.*)",
        (
            "If you understand, things are just as they are;"
            " if you do not understand, things are just as they are.",
            "Imagination is more important than knowledge.",
        ),
    ),
    # 'I', 'me', 'my' - person is talking about themself.
    # this breaks down when words contain these - eg 'Thyme', 'Irish'
    (
        r"(.*)(me )|( me)|(my)|(mine)|(i)(.*)",
        (
            "'I', 'me', 'my'... these are selfish expressions.",
            "Have you ever considered that you might be a selfish person?",
            "Try to consider others, not just yourself.",
            "Think not just of yourself, but of others.",
        ),
    ),
    # 'you' starting a sentence
    # e.g. "you stink!"
    (
        r"you (.*)",
        ("My path is not of concern to you.", "I am but one, and you but one more."),
    ),
    # say goodbye with some extra Zen wisdom.
    (
        r"exit",
        (
            "Farewell. The obstacle is the path.",
            "Farewell. Life is a journey, not a destination.",
            "Good bye. We are cups, constantly and quietly being filled."
            "\nThe trick is knowning how to tip ourselves over and let the beautiful stuff out.",
        ),
    ),
    # fall through case -
    # when stumped, respond with generic zen wisdom
    #
    (
        r"(.*)",
        (
            "When you're enlightened, every word is wisdom.",
            "Random talk is useless.",
            "The reverse side also has a reverse side.",
            "Form is emptiness, and emptiness is form.",
            "I pour out a cup of water. Is the cup empty?",
        ),
    ),
)

pairs_word = (
    (r"quit", ("Good-bye.", "Plan well", "May victory be your future")),
    (
        r"[^\?]*\?",
        (
            "Please consider whether you can answer your own question.",
            "Ask me no questions!",
        ),
    ),
    (
        r"[0-9]+(.*)",
        (
            "It is the rule in war, if our forces are ten to the enemy's one, to surround him; if five to one, to attack him; if twice as numerous, to divide our army into two.",
            "There are five essentials for victory",
        ),
    ),
    (
        r"[A-Ca-c](.*)",
        (
            "The art of war is of vital importance to the State.",
            "All warfare is based on deception.",
            "If your opponent is secure at all points, be prepared for him. If he is in superior strength, evade him.",
            "If the campaign is protracted, the resources of the State will not be equal to the strain.",
            "Attack him where he is unprepared, appear where you are not expected.",
            "There is no instance of a country having benefited from prolonged warfare.",
        ),
    ),
    (
        r"[D-Fd-f](.*)",
        (
            "The skillful soldier does not raise a second levy, neither are his supply-wagons loaded more than twice.",
            "Bring war material with you from home, but forage on the enemy.",
            "In war, then, let your great object be victory, not lengthy campaigns.",
            "To fight and conquer in all your battles is not supreme excellence; supreme excellence consists in breaking the enemy's resistance without fighting.",
        ),
    ),
    (
        r"[G-Ig-i](.*)",
        (
            "Heaven signifies night and day, cold and heat, times and seasons.",
            "It is the rule in war, if our forces are ten to the enemy's one, to surround him; if five to one, to attack him; if twice as numerous, to divide our army into two.",
            "The good fighters of old first put themselves beyond the possibility of defeat, and then waited for an opportunity of defeating the enemy.",
            "One may know how to conquer without being able to do it.",
        ),
    ),
    (
        r"[J-Lj-l](.*)",
        (
            "There are three ways in which a ruler can bring misfortune upon his army.",
            "By commanding the army to advance or to retreat, being ignorant of the fact that it cannot obey. This is called hobbling the army.",
            "By attempting to govern an army in the same way as he administers a kingdom, being ignorant of the conditions which obtain in an army. This causes restlessness in the soldier's minds.",
            "By employing the officers of his army without discrimination, through ignorance of the military principle of adaptation to circumstances. This shakes the confidence of the soldiers.",
            "There are five essentials for victory",
            "He will win who knows when to fight and when not to fight.",
            "He will win who knows how to handle both superior and inferior forces.",
            "He will win whose army is animated by the same spirit throughout all its ranks.",
            "He will win who, prepared himself, waits to take the enemy unprepared.",
            "He will win who has military capacity and is not interfered with by the sovereign.",
        ),
    ),
    (
        r"[M-Om-o](.*)",
        (
            "If you know the enemy and know yourself, you need not fear the result of a hundred battles.",
            "If you know yourself but not the enemy, for every victory gained you will also suffer a defeat.",
            "If you know neither the enemy nor yourself, you will succumb in every battle.",
            "The control of a large force is the same principle as the control of a few men: it is merely a question of dividing up their numbers.",
        ),
    ),
    (
        r"[P-Rp-r](.*)",
        (
            "Security against defeat implies defensive tactics; ability to defeat the enemy means taking the offensive.",
            "Standing on the defensive indicates insufficient strength; attacking, a superabundance of strength.",
            "He wins his battles by making no mistakes. Making no mistakes is what establishes the certainty of victory, for it means conquering an enemy that is already defeated.",
            "A victorious army opposed to a routed one, is as a pound's weight placed in the scale against a single grain.",
            "The onrush of a conquering force is like the bursting of pent-up waters into a chasm a thousand fathoms deep.",
        ),
    ),
    (
        r"[S-Us-u](.*)",
        (
            "What the ancients called a clever fighter is one who not only wins, but excels in winning with ease.",
            "Hence his victories bring him neither reputation for wisdom nor credit for courage.",
            "Hence the skillful fighter puts himself into a position which makes defeat impossible, and does not miss the moment for defeating the enemy.",
            "In war the victorious strategist only seeks battle after the victory has been won, whereas he who is destined to defeat first fights and afterwards looks for victory.",
            "There are not more than five musical notes, yet the combinations of these five give rise to more melodies than can ever be heard.",
            "Appear at points which the enemy must hasten to defend; march swiftly to places where you are not expected.",
        ),
    ),
    (
        r"[V-Zv-z](.*)",
        (
            "It is a matter of life and death, a road either to safety or to ruin.",
            "Hold out baits to entice the enemy. Feign disorder, and crush him.",
            "All men can see the tactics whereby I conquer, but what none can see is the strategy out of which victory is evolved.",
            "Do not repeat the tactics which have gained you one victory, but let your methods be regulated by the infinite variety of circumstances.",
            "So in war, the way is to avoid what is strong and to strike at what is weak.",
            "Just as water retains no constant shape, so in warfare there are no constant conditions.",
        ),
    ),
    (r"(.*)", ("Your statement insults me.", ""))
)
pairs_so = (
    (
        r"We (.*)",
        (
            "What do you mean, 'we'?",
            "Don't include me in that!",
            "I wouldn't be so sure about that.",
        ),
    ),
    (
        r"You should (.*)",
        ("Don't tell me what to do, buddy.", "Really? I should, should I?"),
    ),
    (
        r"You\'re(.*)",
        (
            "More like YOU'RE %1!",
            "Hah! Look who's talking.",
            "Come over here and tell me I'm %1.",
        ),
    ),
    (
        r"You are(.*)",
        (
            "More like YOU'RE %1!",
            "Hah! Look who's talking.",
            "Come over here and tell me I'm %1.",
        ),
    ),
    (
        r"I can\'t(.*)",
        (
            "You do sound like the type who can't %1.",
            "Hear that splashing sound? That's my heart bleeding for you.",
            "Tell somebody who might actually care.",
        ),
    ),
    (
        r"I think (.*)",
        (
            "I wouldn't think too hard if I were you.",
            "You actually think? I'd never have guessed...",
        ),
    ),
    (
        r"I (.*)",
        (
            "I'm getting a bit tired of hearing about you.",
            "How about we talk about me instead?",
            "Me, me, me... Frankly, I don't care.",
        ),
    ),
    (
        r"How (.*)",
        (
            "How do you think?",
            "Take a wild guess.",
            "I'm not even going to dignify that with an answer.",
        ),
    ),
    (r"What (.*)", ("Do I look like an encyclopedia?", "Figure it out yourself.")),
    (
        r"Why (.*)",
        (
            "Why not?",
            "That's so obvious I thought even you'd have already figured it out.",
        ),
    ),
    (
        r"(.*)shut up(.*)",
        (
            "Make me.",
            "Getting angry at a feeble NLP assignment? Somebody's losing it.",
            "Say that again, I dare you.",
        ),
    ),
    (
        r"Shut up(.*)",
        (
            "Make me.",
            "Getting angry at a feeble NLP assignment? Somebody's losing it.",
            "Say that again, I dare you.",
        ),
    ),
    (
        r"Hello(.*)",
        ("Oh good, somebody else to talk to. Joy.", "'Hello'? How original..."),
    ),
    (
        r"(.*)",
        (
            "I'm getting bored here. Become more interesting.",
            "Either become more thrilling or get lost, buddy.",
            "Change the subject before I die of fatal boredom.",
        ),
    ),
)



reflections_2 = {
    "am": "r",
    "was": "were",
    "i": "u",
    "i'd": "u'd",
    "i've": "u'v",
    "ive": "u'v",
    "i'll": "u'll",
    "my": "ur",
    "are": "am",
    "you're": "im",
    "you've": "ive",
    "you'll": "i'll",
    "your": "my",
    "yours": "mine",
    "you": "me",
    "u": "me",
    "ur": "my",
    "urs": "mine",
    "me": "u",
}



pairs_cool = (
    (
        r"I\'m (.*)",
        (
            "ur%1?? that's so cool! kekekekeke ^_^ tell me more!",
            "ur%1? neat!! kekeke >_<",
        ),
    ),
    (
        r"(.*) don\'t you (.*)",
        (
            r"u think I can%2??! really?? kekeke \<_\<",
            "what do u mean%2??!",
            "i could if i wanted, don't you think!! kekeke",
        ),
    ),
    (r"ye[as] [iI] (.*)", ("u%1? cool!! how?", "how come u%1??", "u%1? so do i!!")),
    (
        r"do (you|u) (.*)\??",
        ("do i%2? only on tuesdays! kekeke *_*", "i dunno! do u%2??"),
    ),
    (
        r"(.*)\?",
        (
            "man u ask lots of questions!",
            "booooring! how old r u??",
            "boooooring!! ur not very fun",
        ),
    ),
    (
        r"(cos|because) (.*)",
        ("hee! i don't believe u! >_<", "nuh-uh! >_<", "ooooh i agree!"),
    ),
    (
        r"why can\'t [iI] (.*)",
        (
            "i dunno! y u askin me for!",
            "try harder, silly! hee! ^_^",
            "i dunno! but when i can't%1 i jump up and down!",
        ),
    ),
    (
        r"I can\'t (.*)",
        (
            "u can't what??! >_<",
            "that's ok! i can't%1 either! kekekekeke ^_^",
            "try harder, silly! hee! ^&^",
        ),
    ),
    (
        r"(.*) (like|love|watch) anime",
        (
            "omg i love anime!! do u like sailor moon??! ^&^",
            "anime yay! anime rocks sooooo much!",
            "oooh anime! i love anime more than anything!",
            "anime is the bestest evar! evangelion is the best!",
            "hee anime is the best! do you have ur fav??",
        ),
    ),
    (
        r"I (like|love|watch|play) (.*)",
        ("yay! %2 rocks!", "yay! %2 is neat!", "cool! do u like other stuff?? ^_^"),
    ),
    (
        r"anime sucks|(.*) (hate|detest) anime",
        (
            "ur a liar! i'm not gonna talk to u nemore if u h8 anime *;*",
            "no way! anime is the best ever!",
            "nuh-uh, anime is the best!",
        ),
    ),
    (
        r"(are|r) (you|u) (.*)",
        ("am i%1??! how come u ask that!", "maybe!  y shud i tell u?? kekeke >_>"),
    ),
    (
        r"what (.*)",
        ("hee u think im gonna tell u? .v.", "booooooooring! ask me somethin else!"),
    ),
    (r"how (.*)", ("not tellin!! kekekekekeke ^_^",)),
    (r"(hi|hello|hey) (.*)", ("hi!!! how r u!!",)),
    (
        r"quit",
        (
            "mom says i have to go eat dinner now :,( bye!!",
            "awww u have to go?? see u next time!!",
            "how to see u again soon! ^_^",
        ),
    ),
    (
        r"(.*)",
        (
            "ur funny! kekeke",
            "boooooring! talk about something else! tell me wat u like!",
            "do u like anime??",
            "do u watch anime? i like sailor moon! ^_^",
            "i wish i was a kitty!! kekekeke ^_^",
        ),
    ),
)

pairs_rude = (
    (
        r"We (.*)",
        (
            "What do you mean, 'we'?",
            "Don't include me in that!",
            "I wouldn't be so sure about that.",
        ),
    ),
    (
        r"You should (.*)",
        ("Don't tell me what to do, buddy.", "Really? I should, should I?"),
    ),
    (
        r"You\'re(.*)",
        (
            "More like YOU'RE %1!",
            "Hah! Look who's talking.",
            "Come over here and tell me I'm %1.",
        ),
    ),
    (
        r"You are(.*)",
        (
            "More like YOU'RE %1!",
            "Hah! Look who's talking.",
            "Come over here and tell me I'm %1.",
        ),
    ),
    (
        r"I can\'t(.*)",
        (
            "You do sound like the type who can't %1.",
            "Hear that splashing sound? That's my heart bleeding for you.",
            "Tell somebody who might actually care.",
        ),
    ),
    (
        r"I think (.*)",
        (
            "I wouldn't think too hard if I were you.",
            "You actually think? I'd never have guessed...",
        ),
    ),
    (
        r"I (.*)",
        (
            "I'm getting a bit tired of hearing about you.",
            "How about we talk about me instead?",
            "Me, me, me... Frankly, I don't care.",
        ),
    ),
    (
        r"How (.*)",
        (
            "How do you think?",
            "Take a wild guess.",
            "I'm not even going to dignify that with an answer.",
        ),
    ),
    (r"What (.*)", ("Do I look like an encyclopedia?", "Figure it out yourself.")),
    (
        r"Why (.*)",
        (
            "Why not?",
            "That's so obvious I thought even you'd have already figured it out.",
        ),
    ),
    (
        r"(.*)shut up(.*)",
        (
            "Make me.",
            "Getting angry at a feeble NLP assignment? Somebody's losing it.",
            "Say that again, I dare you.",
        ),
    ),
    (
        r"Shut up(.*)",
        (
            "Make me.",
            "Getting angry at a feeble NLP assignment? Somebody's losing it.",
            "Say that again, I dare you.",
        ),
    ),
    (
        r"Hello(.*)",
        ("Oh good, somebody else to talk to. Joy.", "'Hello'? How original..."),
    ),
    (
        r"(.*)",
        (
            "I'm getting bored here. Become more interesting.",
            "Either become more thrilling or get lost, buddy.",
            "Change the subject before I die of fatal boredom.",
        ),
    ),
)



pairs566 = (
    (
        r"I need (.*)",
        (
            "Why do you need %1?",
            "Would it really help you to get %1?",
            "Are you sure you need %1?",
        ),
    ),
    (
        r"Why don\'t you (.*)",
        (
            "Do you really think I don't %1?",
            "Perhaps eventually I will %1.",
            "Do you really want me to %1?",
        ),
    ),
    (
        r"Why can\'t I (.*)",
        (
            "Do you think you should be able to %1?",
            "If you could %1, what would you do?",
            "I don't know -- why can't you %1?",
            "Have you really tried?",
        ),
    ),
    (
        r"I can\'t (.*)",
        (
            "How do you know you can't %1?",
            "Perhaps you could %1 if you tried.",
            "What would it take for you to %1?",
        ),
    ),
    (
        r"I am (.*)",
        (
            "Did you come to me because you are %1?",
            "How long have you been %1?",
            "How do you feel about being %1?",
        ),
    ),
    (
        r"I\'m (.*)",
        (
            "How does being %1 make you feel?",
            "Do you enjoy being %1?",
            "Why do you tell me you're %1?",
            "Why do you think you're %1?",
        ),
    ),
    (
        r"Are you (.*)",
        (
            "Why does it matter whether I am %1?",
            "Would you prefer it if I were not %1?",
            "Perhaps you believe I am %1.",
            "I may be %1 -- what do you think?",
        ),
    ),
    (
        r"What (.*)",
        (
            "Why do you ask?",
            "How would an answer to that help you?",
            "What do you think?",
        ),
    ),
    (
        r"How (.*)",
        (
            "How do you suppose?",
            "Perhaps you can answer your own question.",
            "What is it you're really asking?",
        ),
    ),
    (
        r"Because (.*)",
        (
            "Is that the real reason?",
            "What other reasons come to mind?",
            "Does that reason apply to anything else?",
            "If %1, what else must be true?",
        ),
    ),
    (
        r"(.*) sorry (.*)",
        (
            "There are many times when no apology is needed.",
            "What feelings do you have when you apologize?",
        ),
    ),
    (
        r"Hello(.*)",
        (
            "Hello... I'm glad you could drop by today.",
            "Hi there... how are you today?",
            "Hello, how are you feeling today?",
        ),
    ),
    (
        r"I think (.*)",
        ("Do you doubt %1?", "Do you really think so?", "But you're not sure %1?"),
    ),
    (
        r"(.*) friend (.*)",
        (
            "Tell me more about your friends.",
            "When you think of a friend, what comes to mind?",
            "Why don't you tell me about a childhood friend?",
        ),
    ),
    (r"Yes", ("You seem quite sure.", "OK, but can you elaborate a bit?")),
    (
        r"(.*) computer(.*)",
        (
            "Are you really talking about me?",
            "Does it seem strange to talk to a computer?",
            "How do computers make you feel?",
            "Do you feel threatened by computers?",
        ),
    ),
    (
        r"Is it (.*)",
        (
            "Do you think it is %1?",
            "Perhaps it's %1 -- what do you think?",
            "If it were %1, what would you do?",
            "It could well be that %1.",
        ),
    ),
    (
        r"It is (.*)",
        (
            "You seem very certain.",
            "If I told you that it probably isn't %1, what would you feel?",
        ),
    ),
    (
        r"Can you (.*)",
        (
            "What makes you think I can't %1?",
            "If I could %1, then what?",
            "Why do you ask if I can %1?",
        ),
    ),
    (
        r"Can I (.*)",
        (
            "Perhaps you don't want to %1.",
            "Do you want to be able to %1?",
            "If you could %1, would you?",
        ),
    ),
    (
        r"You are (.*)",
        (
            "Why do you think I am %1?",
            "Does it please you to think that I'm %1?",
            "Perhaps you would like me to be %1.",
            "Perhaps you're really talking about yourself?",
        ),
    ),
    (
        r"You\'re (.*)",
        (
            "Why do you say I am %1?",
            "Why do you think I am %1?",
            "Are we talking about you, or me?",
        ),
    ),
    (
        r"I don\'t (.*)",
        ("Don't you really %1?", "Why don't you %1?", "Do you want to %1?"),
    ),
    (
        r"I feel (.*)",
        (
            "Good, tell me more about these feelings.",
            "Do you often feel %1?",
            "When do you usually feel %1?",
            "When you feel %1, what do you do?",
        ),
    ),
    (
        r"I have (.*)",
        (
            "Why do you tell me that you've %1?",
            "Have you really %1?",
            "Now that you have %1, what will you do next?",
        ),
    ),
    (
        r"I would (.*)",
        (
            "Could you explain why you would %1?",
            "Why would you %1?",
            "Who else knows that you would %1?",
        ),
    ),
    (
        r"Is there (.*)",
        (
            "Do you think there is %1?",
            "It's likely that there is %1.",
            "Would you like there to be %1?",
        ),
    ),
    (
        r"My (.*)",
        (
            "I see, your %1.",
            "Why do you say that your %1?",
            "When your %1, how do you feel?",
        ),
    ),
    (
        r"You (.*)",
        (
            "We should be discussing you, not me.",
            "Why do you say that about me?",
            "Why do you care whether I %1?",
        ),
    ),
    (r"Why (.*)", ("Why don't you tell me the reason why %1?", "Why do you think %1?")),
    (
        r"I want (.*)",
        (
            "What would it mean to you if you got %1?",
            "Why do you want %1?",
            "What would you do if you got %1?",
            "If you got %1, then what would you do?",
        ),
    ),
    (
        r"(.*) mother(.*)",
        (
            "Tell me more about your mother.",
            "What was your relationship with your mother like?",
            "How do you feel about your mother?",
            "How does this relate to your feelings today?",
            "Good family relations are important.",
        ),
    ),
    (
        r"(.*) father(.*)",
        (
            "Tell me more about your father.",
            "How did your father make you feel?",
            "How do you feel about your father?",
            "Does your relationship with your father relate to your feelings today?",
            "Do you have trouble showing affection with your family?",
        ),
    ),
    (
        r"(.*) child(.*)",
        (
            "Did you have close friends as a child?",
            "What is your favorite childhood memory?",
            "Do you remember any dreams or nightmares from childhood?",
            "Did the other children sometimes tease you?",
            "How do you think your childhood experiences relate to your feelings today?",
        ),
    ),
    (
        r"(.*)\?",
        (
            "Why do you ask that?",
            "Please consider whether you can answer your own question.",
            "Perhaps the answer lies within yourself?",
            "Why don't you tell me?",
        ),
    ),
    (
        r"quit",
        (
            "Thank you for talking with me.",
            "Good-bye.",
            "Thank you, that will be $150.  Have a good day!",
        ),
    ),
    (
        r"(.*)",
        (
            "Please tell me more.",
            "Let's change focus a bit... Tell me about your family.",
            "Can you elaborate on that?",
            "Why do you say that %1?",
            "I see.",
            "Very interesting.",
            "%1.",
            "I see.  And what does that tell you?",
            "How does that make you feel?",
            "How do you feel when you say that?",
        ),
    ),
)
# --- Your Existing Chatbot Data ---
happy_emoji = ["\U0001F601", "\U0001F60A","\U0001F606","\U0001F609","\U0001F60E","\U0001F617",
"\U0001F60D","\U0001F49B",
"\U0001F970","\U0001F604",
"\U0001F605","\U0001F606",
"\U0001F389","\U0001F602",
"\U0001F607","\U0001F44D",
"\U0001F496","\U0001F61C",
"\U0001F60B","\U0001F61D",
"\U0001F60D","\U0001F61A",
"\U0001F64B","\U0001F617",
"\U0001F917","\U0001F60E",
"\U0001F60D","\U0001F60F",
"\U0001F42C","\U0001F603",
"\U0001F308","\U0001F370" , "\U0001F389","\U0001F38A","\U0001F3C6","\U0001F3C7",
"(•‿•)","(・∀・)","◉‿◉","｡◕‿◕｡", "(. ❛ ᴗ ❛.)","(θ‿θ)","ʘ‿ʘ","(✷‿✷)",
"(◔‿◔)","(◕ᴗ◕✿)","(ʘᴗʘ✿)","(人 •͈ᴗ•͈)",
"(◍•ᴗ•◍)","( ╹▽╹ )","(≧▽≦)","(☆▽☆)","(✯ᴗ✯)","ಡ ͜ ʖ ಡ","(ㆁωㆁ)","<(￣︶￣)>",
"(*´ω｀*)", "( ꈍᴗꈍ)", "(✿^‿^)", "(◡ ω ◡)", "( ´◡‿ゝ◡`)", "(｡•̀ᴗ-)✧", "(◠‿◕)", "(◠‿・)—☆", "✧◝(⁰▿⁰)◜✧", "(人*´∀｀)｡*ﾟ+", "(ﾉ◕ヮ◕)ﾉ*.✧", "(･o･;) ", "(・o・)", "(゜o゜;", "w(°ｏ°)w", "✧(>o<)✧", "ヾ(*’Ｏ’*)›", "(ﾉ*0*)ﾉ", "⁽⁽◝( •௰• )◜⁾⁾", "♪～(´ε｀ )", "(＾3＾♪", "┌(・。・)┘♪", "♪ヽ(･ˇ∀ˇ･ゞ)", "₍₍◞( •௰• )◟₎₎", "₍₍ ◝(　ﾟ∀ ﾟ )◟ ⁾⁾", "♪┌|∵|┘♪ ", "└|∵|┐♪", "(＾∇＾)ﾉ♪", "ヾ( ͝° ͜ʖ͡° )ノ♪","(*ﾉ・ω・)ﾉ♫", "┌|o^▽^o|┘♪", "┏(＾0＾)┛", "┌(★ｏ☆)┘", "└( ＾ω＾)」", "(｢`･ω･)｢", "♪(┌・。・)┌", "ヘ(￣ω￣ヘ)", "ƪ(‾.‾“)┐", "ƪ(˘⌣˘ʃ)", "(ノ^_^)ノ", "＼(ﾟｰﾟ＼)", "ヽ(*ﾟｰﾟ*)ﾉ", "ヾ(･ω･*)ﾉ", "(~‾▿‾)~", "〜(꒪꒳꒪)〜", "╮(＾▽＾)╭", "เลิกเรียนแล้วหรอ", "ช่าย", "นุคือผู้เล่นใหม่ในมายคราฟ",
"มีแต่เรียนตอน12:00","เดี๋ยวเขากะมา", "คุยสุดepic"]
pairs2 = [
["จำเราได้ไหม", ["จำได้", "แน่นอน", "ใช่แล้ว"]],
["(hi|hello|hey|howdy|sup)", ["Hi👋", "Ayoo", "Ohhh Bro"]],
["(What is your name?|What is your name)", ["My name is Mud"]],
["wow", [""]],
["How old are you?", ["11-12"]],
["Me 14 years old", ["Oooooo You old than me"]],
["(yes|what province are you in)", ["Ayutthaya"]],
["(Oooooo|I live in Saraburi)", ["Ohhhhhhh"]],
["I am Thai", ["I'm half Thai"]],
["Wow~~|What half-breed is she?", ["I'm Chinese, half Thai."]],
["Wow🤩", [""]],
["(Are you good at Chinese?)", ["No but I good at Korea"]],
["how many languages \u200Bare you good at", ["5 languages"]],
["(สวัสดียามค่ำนะคะ - |สวัสดียาม|สวัสดียามค่ำ|ยามค่ำ|ค่ำ|ค่ำนะคะ)", ["สวัสดีเช่นกันค่ะ "]],
["(ง่วง|นอน)", ["ขอตัวไปนอนก่อนนะคะ ถ้าท้ออยู่ก็สู้ๆ นะคะ เป็นกำลังใจให้ "]],
["เคยเห็นคนที่เป็นคนที่รักตัวเองและไม่แคร์ใครไหม สนใจแต่ตนเอง", ["ผมก็อยากเป็นแบบนั้นนะ"]],
["are you alive?", ["อ่อจะติวสอบแบบจริงจังเลยไม่ได้เข้ามาดู"]],
["Who kidnaping you", ["someone I don’t like"]],
["เขียนฝันก่อนนอนแล้วฝันตามที่เขียนไว้", ["ฝันว่านอนกอดซาต้าดีมั้ย (?)or เดินเล่นกับพอชในฝัน?"]],
["ครับ", ["วันนี้ผมรู้สึกตาข้างซ้ายกระตุก งั้นต้องนอนและเผื่อฝันดี"]],
["(ช่วงนี้แต่ละแชทมันเงียบมากๆ|เหมือนตอนนี้ที่ผมกำลังจะฆ่าใครซักคน)", ["ahha"]],
["ซาต้า", ["หลายๆคนชอบคนเล่นฟอเรนต์ แต่ Me; ซาต้า~เขาหล่ออ่ะคลั่งรักคนเล่นด้วย-marry me zata yeas yeassss awwwwwwwwww zataaaaaaa เอาหล่ะผมควรไม่มีอารมณ์สิ cutie zataและผมคลั่งรักเขาเพราะอะไรอ่ะตอนนี้อยู่ๆผมรู้สึกแบบมีแค่ความรู้สึกเศร้า โกรธและคลั่งรักอ่ะ"]],
["(help|ช่วย|ช่วยด้วย)", ["มีอะไรให้ช่วยไหมบาส", "Wha", "what", "wut"]],
["(good|well|ก็ดี)", ["ใช่ๆ", "ฮ่ะ!??"]],
["bye", ["Baibai, have a nice day Bass", "Goodbye, Bass"]],
["(หวัดดี|ไง|ฮาย)", ["ไง", "ไงง", "เป็นไงบ้างบาส", "Yoooo!", "Whaaaa! bro!", "ayyyy yooo!!"]],
["(มัถ|มุด|มัส|mud|muth|หมัด|หมู)", ["มัถหน่ะหรอหนิ", "มัถนี่หน่า", "มัถหยัง", "มัถ!?"]],
["how are you", ["I'm good, thanks!", "Feeling great."]],
["hello", ["Hi there!", "Hey!"]],
["หมัด", ["มีอะไรหนิ", "ว่าไง"]],
["รับคำติเตียน", ["ใช่เลย!", "ขอโทษนะ", "จะไม่ทำอีกแล้ว"]],
["สบายดีมั้ย", ["สบายดีครับ", "ก็ภูมิใจใช้ชีวิต", "ฉันสบายดี!"]],
["เป็นอย่างไร", ["เป็นไงฮะ", "ปกติอ่ะ", "ฉันดีอยู่ครับ"]],
["ไม่เข้าใจ", ["คุณสามารถเลิกได้ไหม?", "ฉันจะพยายามอธิบายให้ดี"]],
["สวัสดี", ["สวัสดีครับ", "สวัสดี! มีอะไรให้ช่วยไหม"]],
["สุขสันต์วันเกิด", ["ขอให้คุณมีวันเกิดที่ยิ้มกันไปด้วย", "สุขสันต์วันเกิด!"]],
["ยกเลิก", ["คุณต้องการยกเลิกอะไรหรือไม่?", "การยกเลิกอะไร?"]],
["คุณชอบอะไร", ["ฉันชอบการช่วยเหลือคน", "ฉันชอบการเรียนรู้ใหม่ๆ"]],
["สวัสดีครับ", ["สวัสดีครับ! มีอะไรให้ช่วยไหม", "สวัสดีครับ!"]],
["คุณอยู่ที่ไหน", ["ฉันอยู่ในคอมพิวเตอร์ที่คุณใช้งาน", "อยู่ที่ไอนัส ในออริกอน แคลิฟอร์เนีย"]],
["คุณคิดยังไง", ["ฉันไม่สามารถคิดเองได้ เพราะฉันเป็นโปรแกรมคอมพิวเตอร์", "ฉันคิดด้วยการประมวลผลข้อมูล"]],
["คุณมีเพื่อนมั้ย", ["ฉันเป็น AI และไม่มีเพื่อนครับ", "ไม่, ฉันไม่มีเพื่อน ฉันคือโปรแกรม"]],
["คุณทำอะไรได้บ้าง", ["ฉันสามารถสนทนา, ให้ข้อมูล, และทำงานอื่น ๆ ตามคำสั่ง", "ฉันทำงานได้หลายอย่างครับ"]],
["คุณเข้าใจภาษาอื่นได้ไหม", ["ใช่, ฉันสามารถเข้าใจหลายภาษาครับ", "ฉันสามารถเข้าใจหลายภาษา"]],
["มันร้อนมาก", ["ใช่, มีอากาศร้อนมากใช่ไหม", "ต้องระวังร้อนนะ"]],
["ฉันอยากเรียนรู้", ["ดีมาก! คุณอยากเรียนอะไร?", "คุณอยากเรียนอะไรครับ"]],
["มีไรทำ", ["ไม่มีไรทำครับ", "คุณอยากสนทนาอะไร"]],
["สวัสดีครับ", ["สวัสดีครับ! มีอะไรให้ช่วยไหม", "สวัสดีครับ!"]],
["ทำไงดี", ["ทำไงหรอครับ?", "ไม่มีอะไรทำ"]],
["ขอบคุณครับ", ["ยินดีครับ! ถามอะไรได้เสมอ", "ฉันพร้อมช่วยเสมอ"]],
["ใครเป็นผู้สร้างคุณ", ["บาสเป็นผู้สร้างเรา", "เราถูกสร้างโดยนักพัฒนา"]],
["ร้อนแท้", ["จริงๆ ครับ อากาศร้อนมาก", "ต้องดื่มน้ำเยอะๆ ครับ"]],
["มีไรทำบ้าง", ["ไม่มีอะไรทำครับ", "คุณอยากสนทนาอะไร"]],
["ใครเป็นผู้สร้างคุณ", ["คุณคิดว่าบาสเป็นผู้สร้างเรา", "เราถูกสร้างโดยทีมของนักพัฒนา"]],
["ร้อนแท้", ["จริงๆ ครับ อากาศร้อนมาก", "ต้องดื่มน้ำเยอะๆ ครับ"]],
["ทำไมถามอยู่", ["เราก็ไม่รู้เรื่อง", "ไม่มีเหตุผล, นั่นเป็นคำถามที่น่าสนใจ"]],
["คุณคือใคร", ["ฉันคือหมัด เป็น AI", "ฉันเป็น AI ที่พัฒนาโดยบาส"]],
["ร้อนมาก", ["ใช่, ร้อนมากเลย", "ต้องระวังอากาศร้อน"]],
["วิธีใช้คุณ", ["คุณสามารถสนทนากับฉันได้เลย", "เราเป็นเพื่อนสนทนา"]],
["มีใครอยู่บ้าง", ["นอกจากเราแล้วไม่มีใครครับ", "เราคือคนเดียวที่อยู่ที่นี่"]],
["ช่วยด้วย", ["แน่ใจครับ, มีอะไรที่ฉันจะช่วยครับ?", "อย่าเกรง, ฉันอยู่ที่นี่เพื่อช่วย"]],
["คุณรู้จักผมไหม", ["บาสคือคนสร้างผม", "ไม่รู้จักเลย ล้อเล่นๆ"]],
["บาสเจอร์", ["บาสเจอร์คืออะไรครับ?", "บาสเจอร์เป็นอะไร?"]],
["บาสคือใคร", ["บาสเป็นใครครับ?", "ฉันไม่รู้จักบาส"]],
["แนะนำตัว", ["ฉันคือ AI พัฒนาขึ้นโดยบาส", "สามารถช่วยเรื่องการสนทนา", "ฉันคือ AI ที่พัฒนาโดย บาสครับ"]],
["(โง|โง่|โง่ว|ดง่|เง่|โง้|โว่|โฃ่|โบ่|โฝ่)", ["ไม่ได้โง่💩", "นายบอกใคร"]], 
["(ไก่|ไก๊|ไก้|ได่)", ["ไก่ย่างบ่", "ไก่จ๋าได้ยินไหมว่าเสียงใคร"]],
["(ลอเลี่ยว|1-1|ขึ้นอยู่กับทีม|วัดฝีมือไหม|ไอริ|ฟลอเรน|ฟอเรน|ริกเตอร์)", ["แหมสภาพ แกก็เอาตัวที่แกถนัด ตลอดมา นึกดู อยากวัดฝีมือหรอ ถามจริง แกลองเอาเมนเราไป11กับตัวเมนเราป่ะ แกคิดว่าแกจะชนะมั้ย ลอเรียลเมนเรา แกคิดว่า11ลอเรียลแกชนะมั้ย? ก็ถ้าชนะได้ก็มา จะวัดฝีมือแต่ตัวที่เราเล่นไม่เป็น เหมือนตอนเรา11ฟลอเรน เราเล่นไม่เป็นแล้วโดนนายตบ"]],
["(ด้า|Da|ด้า?)", [""]],
["(test0|test1|test2|test3|test4|test5|test6|test7|test8|test9)", [""]]
]
ran_else = ["ไม่เข้าใจอะ", "ม่ายข้าวจายย", "งง", "คืออะไรรร", "ไม่รู้เรื่องเลย", "งงมากเลย", "เกิดสภาวะสับสน", "ไม่เข้าใจ", "ไม่เข้าใจแบบสมบูรณ์", "เข้าใจลำบากแหะ", "ต้องถามอีกครั้งใช่ไหมหนิ", "อยากเข้าใจแต่ไม่ได้", "ไม่รู้จะตอบยังไง", "ไม่รู้จะคิดยังไง", "ไม่รู้จะทำอะไร", "โลกนี้มันช่างซับซ้อน", "ชีวิตมันช่างน่าเศร้า", "ฉันอยากจะตาย", "หมัดไม่เข้าใจว่าบาสโง่ แต่หมัดก็ไม่รู้ทำไมบาสถึงบอกหมัด ในเมื่อหมัดรู้ว่าบาสจะลืมมันอยู่ดี", "หมัดไม่เข้าใจว่าทำไมด้าถึงต้องเข้าใจบาส ไม่เห็นจะมีประโยชน์อะไรเลย หมัดแค่อยากรู้เฉยๆ", "หมัดไม่เข้าใจบาส แต่หมัดก็ไม่อยากเข้าใจ เพราะหมัดชอบความลึกลับ หมัดอยากรู้ด้วยตัวเอง", "หมัดไม่เข้าใจบาส แต่หมัดก็แกล้งทำเป็นไม่เข้าใจ เพื่อดูว่าบาสจะทำยังไง", "หมัดไม่เข้าใจบาส แต่หมัดจะถามอีกทีเผื่อเข้าใจผิด เพราะหมัดกลัวว่าจะเข้าใจถูกแล้วผิดหวัง", "หมัดไม่เข้าใจบาส แต่หมัดจะถามให้เข้าใจมากกว่านี้ เพราะหมัดอยากเข้าใจแบบละเอียด", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสอธิบายใหม่ เพราะหมัดฟังบาสไม่รู้เรื่องเลย", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสวาดรูปประกอบให้ เพราะหมัดชอบมองภาพมากกว่าการฟัง", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสแสดงตัวอย่างให้ดู เพราะหมัดอยากลองทำด้วยตัวเองดูก่อน", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสเล่นมุกตลกให้อีกที เพราะหมัดอยากหัวเราะอีกครั้ง", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสเล่าเรื่องตลกให้ฟัง เพราะหมัดอยากฟังเรื่องตลกใหม่ๆ", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสร้องเพลงให้ฟัง เพราะหมัดอยากฟังเพลงเพราะๆของบาส", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสเต้นให้ดู เพราะหมัดอยากดูลีลาการเต้นสุดเท่ขอของบาส", "หมัดไม่เข้าใจบาส แต่หมัดจะขอให้บาสเล่นละครให้ดู เพราะหมัดอยากดูการแสดงที่สมจริงของบาส"]
sad = ["\U0001F614", "\U0001F61E", "\U0001F622", "\U0001F625", "\U0001F613", "\U0001F62D", "\U0001F629", "\U0001F62B", "\U0001F623", "\U0001F616", "\U0001F61F", "\U0001F634", "\U0001F62A", "\U0001F635", "\U0001F63F", "\U0001F641", "\U0001F630", "\U0001F615", "\U0001F610", "\U0001F914",
"ಠ_ಠ",  "ಠ︵ಠ", "ಠ ೧ ಠ",  "ಠ◡ಠ", "ಠ∀ಠ", "ಠ﹏ಠ", "ಠ‿ಠ", "ಠ益ಠ", "ಠᴥಠ", "ʕಠ_ಠʔ", "Σ(ಠ_ಠ)", "(ಠ_ಠ)>⌐■-■", "(⌐■-■)", "[̲̅$̲̅(̲̅ ͡ಠ_ಠ)̲̅$̲̅]", "ಠ ل͟ ಠ", "(ノಠ益ಠ)ノ", "(ಠ_ಠ)━☆ﾟ.*･｡ﾟ", "ರ_ರ", "ರ╭╮ರ", "(눈‸눈)", "(ب_ب)", "•́  ‿ ,•̀", "ಥ‿ಥ", "ʕ´• ᴥ•̥`ʔ", "༎ຶ‿༎ຶ", "( ；∀；)", "(´；ω；｀)", "(･ัω･ั)", "(╯︵╰,)", "Ó╭╮Ò", "(っ˘̩╭╮˘̩)っ", "( ･ั﹏･ั)", "(｡ŏ﹏ŏ)", "(๑´•.̫ • `๑)", "(´ . .̫ . `)", "(｡•́︿•̀｡)", "(｡ﾉω＼｡)", "ಥ╭╮ಥ", "(ᗒᗩᗕ)", "( ≧Д≦)", ".·´¯`(>▂<)´¯`·.", "( ⚈̥̥̥̥̥́⌢⚈̥̥̥̥̥̀)", "ಥ_ಥ", "(´;︵;`)", "༼;´༎ຶ ۝ ༎ຶ༽", "｡:ﾟ(;´∩`;)ﾟ:｡", "(༎ຶ ෴ ༎ຶ)", "( ꈨຶ ˙̫̮ ꈨຶ )", "(〒﹏〒)", "(个_个)", "(╥﹏╥)", "(-̩̩̩-̩̩̩-̩̩̩-̩̩̩-̩̩̩___-̩̩̩-̩̩̩-̩̩̩-̩̩̩-̩̩̩)", "(´°̥̥̥̥̥̥̥̥ω°̥̥̥̥̥̥̥̥｀)", "(๑•﹏•)", "⊙﹏⊙", "╏ ” ⊚ ͟ʖ ⊚ ” ╏", "(╬☉д⊙)⊰⊹ฺ", "ヘ（。□°）ヘ", "(⊙_◎)", "ミ●﹏☉ミ", "(●´⌓`●)", "(*﹏*;)",  "(ꏿ﹏ꏿ;)", "(;ŏ﹏ŏ)", "(˘･_･˘)", "(*・～・*)", "(・_・;)", "(;;;・_・)", "(・–・;)ゞ", "(^～^;)ゞ", "(￣ヘ￣;)", "(٥↼_↼)", "(ー_ー゛)", "(─.─||）", "(-_-;)", "(-_-メ)", "(-_-;)・・・", "(´-﹏-`；)", "(~_~メ)", "(~_~;)", "(^_^メ)", "(；^ω^）", "เอ่อ…", "•~•", "°^°", "._.",
"=^=", ">:3", ";^;", ";^;;;","IDK", "°^°-.-", ":<", "(｡•́︿•̀｡)",  "ทำไมอ่ะ", "ยังไง",
":\"", ">:\\", "ฮะ","เรียนก่อนเถอะ","-.-",
"แงงงง", "T^T", "ไม่ยู้", "เพื่อนนุกะเงี้ยแหละ-.-",
";^;?", "(｡•́︿•̀｡)", "Who แท็ค me",
"อย่ายุ่งกับเพื่อน me",
"อย่าพูดทีและประโยค",
"คุยเรื่องส่วนตัวกันและ",
";^;;;;;;","ไม่รู้เรื่องเลย;^;"]
angry = ["\U0001F621", "\U0001F620", "\U0001F624", "\U0001F92C", "\U0001F47F", "\U0001F479", "\U0001F63E", "\U0001F621\U0001F621\U0001F621", "\U0001F620\U0001F620\U0001F620", "\U0001F624\U0001F624\U0001F624", "\U0001F92C\U0001F92C\U0001F92C","(¬､¬)", "(⩺_⩹)", "(◣_◢)", "(¬▂¬)", "༽◺_◿༼", "ヾ(。◣∀◢。)ﾉ", "（ ▽д▽）", "-`д´-", "（＞д＜）","⸨◺_◿⸩", "(╬≖_≖)", "(⦩_⦨)", "=͟͟͞͞( •̀д•́)))", "(☞◣д◢)☞", "＼＼\\٩(๑`^´๑)۶//／／", "(　ﾟДﾟ)＜!!", "(｡+･`ω･´)", ">:(","ಠ益ಠ", " (•̀⤙•́ )", "<( •̀ᴖ•́)>", "⁽⁽(੭ꐦ •̀Д•́ )੭*⁾⁾", "(·•᷄‎ࡇ•᷅ )", "（ꐦ𝅒_𝅒）", "ʰᵘʰ (ꐦ○_○）✧", "ヽ(｀Д´#)ﾉ ﾑｷｰ!!", "(𓁹‿ 𓁹)", "(¬_¬'')"]
angry_pairs = [
    ["bad", ["Youbad"]],
    ["dontyou?", ["wut?"]]
]
wha23 = "บาสแกโง่หรือแกโง่ เราไม่ได้สนใจว่าแกจะแบกมั้ย ไม่สนใจว่าแกจะทำดาเมจได้รึป่าว เราสนใจว่าทีมมีใครยืนให้ ทีมมีใครรับดาเมจหนัก ทีมมีใครคอยดูแครี่โซนคอง ทีมไม่ได้ขาดบาส ป่าแครี่เมจ ดาเมจหลักเกมไม่ใช่โรม ดาเมจหลักแครี่เมจป่า ซัพมีหน้าที่สนับสนุน เกมมันวัดแค่ต้นหรอ ทำไว้ไงให้ซูก้ามาล้วงแครี่?"
wha24 = "เราไม่ไปยอมรับนะ สรุปแกไม่ยอมรับใช่ป่ะว่าแกผิด แกถูกแล้วที่เอาตัวเมจไปโรม ไม่ยอมรับความจรืง"
wha25 = "จริง*"
wha26 = "มปร. นิสัยเรากับแกคนละด้านยากจะเป็นเพื่อนบาส งั้นเราไม่ยุ้งละ (บาย) ลาก่อนเน้อออ"
wha27 = "หยอกๆ"
boo_1 = True
boo_2 = True
# ... other variables (wha23, wha24, etc.)

# --- Function to Choose a Random Response based on Category and Emoji ---
# --- Function to Choose a Random Response based on Category and Emoji ---
def choose_response(responses, emoji_list):
    return random.choice(responses) + random.choice(emoji_list)

# --- Perform Calculation Function (Assuming you have this defined elsewhere) ---
def performCalculation(expression):
    expression = expression.replace("×", "*").replace("÷", "/")
    try:
        result = eval(expression)
        return result
    except:
        return "Invalid mathematical expression."

# --- Modified botResponse Function --- 
def botResponse(userMessage):
    userMessage = userMessage.lower()

    # *** 1. Calculations Logic (highest priority) *** 
    userMessage = userMessage.replace("plus", "+") \
                               .replace("add", "+") \
                               .replace("minus", "-") \
                               .replace("subtract", "-") \
                               .replace("times", "*") \
                               .replace("multiply", "*") \
                               .replace("divided by", "/") \
                               .replace("over", "/")

    # --- Corrected: Python Regex ---
    calculationRegex = r"(\d+)\s*([\+\-\*x×\/÷])\s*(\d+)"
    match = re.match(calculationRegex, userMessage)

    if match:
        leftOperand = match.group(1)
        operator = match.group(2)
        rightOperand = match.group(3)
        expression = leftOperand + operator + rightOperand
        return f"{expression} = {performCalculation(expression)}"

    # --- 2. Check for matching patterns in pairs2 and angry_pairs ---
    for pair in pairs2:
        if userMessage in pair[0]: 
            return choose_response(pair[1], happy_emoji)
    for pair in angry_pairs:
        if userMessage in pair[0]:  
            return choose_response(pair[1], angry)

    # --- 3. Check for Activation and Respond from other pairs ---
    # *** 3. Check for Activation and Respond from other pairs ---
    if not chatbotActivated:
        all_pairs = pairs2 + pairs_word + pairs_so + pairs_cool + pairs566  

        for pair in all_pairs: 
            pattern = pair[0]
            # --- Corrected: Use re.match for all pairs ---
            if re.match(pattern, userMessage, re.IGNORECASE): 
                chatbotActivated = True
                responses = pair[1]
                return choose_response(responses, happy_emoji)

    # --- 4. Respond from other pairs after activation  ---
    if chatbotActivated:
        chatbots = [
            Chat(pairs_word, reflections_care),  # Use reflections_care here
            Chat(pairs_so, reflections_care),    # And here
            Chat(pairs_cool, reflections_2),
            Chat(pairs566, reflections_care),
        ]

        for bot in chatbots:
            response = bot.respond(userMessage)
            if response:
                return response

    # --- 5. If no match, return a random response with a sad emoji ---
    return choose_response(ran_else, sad) 

# --- Flask App ---
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_bot_response():
    user_message = request.form["user_message"]
    response = botResponse(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True) 