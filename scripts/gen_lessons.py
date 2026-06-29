#!/usr/bin/env python3
"""Generate src/content/lessons.ts with 50 B1/B2 lessons."""
import json, re, os

# Each topic: (id, level, title_pl, summary_pl, core_vocab[10], dialogs[2], grammar(1), quiz_seed[5], extras{vocab:10, dialog:1, idioms:2})
# vocab tuple: (en, ipa, pl_pron, pl_meaning, example_en)
# dialog: list of (speaker, en, pl)
# grammar: (title, rule_pl, [example_en, ...])

# ---- Shared vocabulary pool to pad each lesson to 25 ----
COMMON_VOCAB = [
    ("achieve","əˈtʃiːv","aczijw","osiągnąć","She wants to achieve her career goals this year."),
    ("afford","əˈfɔːd","afoord","pozwolić sobie (finansowo)","I can't afford a new car right now."),
    ("appreciate","əˈpriːʃieɪt","apriszijejt","doceniać","I really appreciate your help."),
    ("argue","ˈɑːɡjuː","aagju","kłócić się / argumentować","They argue about money all the time."),
    ("assume","əˈsjuːm","asjuum","zakładać","Don't assume he knows the answer."),
    ("attempt","əˈtempt","atempt","próbować / próba","This is my third attempt to pass the exam."),
    ("attitude","ˈætɪtjuːd","atitjuud","postawa / nastawienie","She has a positive attitude to work."),
    ("avoid","əˈvɔɪd","awojd","unikać","Try to avoid sugar in the evening."),
    ("aware","əˈweə","aueə","świadomy","Are you aware of the new rules?"),
    ("borrow","ˈbɒrəʊ","boroł","pożyczać (od kogoś)","Can I borrow your pen?"),
    ("complain","kəmˈpleɪn","kompleejn","narzekać","He always complains about the weather."),
    ("complete","kəmˈpliːt","komplijt","kompletny / ukończyć","I completed the report on time."),
    ("consider","kənˈsɪdə","konsidə","rozważać","We should consider all options."),
    ("convince","kənˈvɪns","konwins","przekonać","She convinced me to go."),
    ("decision","dɪˈsɪʒn","disyżn","decyzja","It was a hard decision."),
    ("decrease","dɪˈkriːs","dikriis","spadek / zmniejszać","Sales decreased last month."),
    ("deserve","dɪˈzɜːv","dizyrw","zasługiwać","You deserve a break."),
    ("disappointed","ˌdɪsəˈpɔɪntɪd","disapojntyd","rozczarowany","I'm disappointed with the result."),
    ("encourage","ɪnˈkʌrɪdʒ","inkarydż","zachęcać","My boss encourages us to learn."),
    ("enough","ɪˈnʌf","inaf","wystarczająco","We have enough time."),
    ("expect","ɪkˈspekt","ekspekt","oczekiwać","I expect you to be on time."),
    ("experience","ɪkˈspɪəriəns","ekspirjens","doświadczenie","She has ten years of experience."),
    ("explain","ɪkˈspleɪn","ekspleejn","wyjaśniać","Can you explain it again?"),
    ("focus","ˈfəʊkəs","foukas","skupiać się","I can't focus when it's loud."),
    ("improve","ɪmˈpruːv","impruuw","poprawiać (się)","I want to improve my English."),
    ("increase","ɪnˈkriːs","inkriis","wzrost / zwiększać","Prices have increased again."),
    ("instead","ɪnˈsted","insted","zamiast","Let's take the train instead."),
    ("issue","ˈɪʃuː","iszju","problem / sprawa","There's an issue with my account."),
    ("manage","ˈmænɪdʒ","menydż","zarządzać / dawać radę","She manages a small team."),
    ("mention","ˈmenʃn","menszn","wspomnieć","He didn't mention his plans."),
    ("notice","ˈnəʊtɪs","noutys","zauważyć / wypowiedzenie","I didn't notice the change."),
    ("offer","ˈɒfə","ofə","oferować / oferta","They offered me a new job."),
    ("opportunity","ˌɒpəˈtjuːnəti","opətjuunyti","okazja / szansa","Don't miss this opportunity."),
    ("prefer","prɪˈfɜː","prifyr","woleć","I prefer tea to coffee."),
    ("prepare","prɪˈpeə","pripeə","przygotować","I need to prepare for the meeting."),
    ("prevent","prɪˈvent","priwent","zapobiegać","Wash your hands to prevent illness."),
    ("provide","prəˈvaɪd","prowajd","zapewniać","We provide free training."),
    ("realise","ˈrɪəlaɪz","riəlajz","zdać sobie sprawę","I didn't realise it was so late."),
    ("recommend","ˌrekəˈmend","rekomend","polecać","I recommend this restaurant."),
    ("reduce","rɪˈdjuːs","ridjuus","redukować / zmniejszać","We need to reduce costs."),
    ("rely","rɪˈlaɪ","rilaj","polegać na","You can rely on me."),
    ("require","rɪˈkwaɪə","rikłajə","wymagać","This job requires patience."),
    ("succeed","səkˈsiːd","saksiid","odnieść sukces","She succeeded in her career."),
    ("suggest","səˈdʒest","sadżest","sugerować / proponować","Can I suggest something?"),
    ("support","səˈpɔːt","sapoort","wspierać / wsparcie","Thanks for your support."),
    ("though","ðəʊ","dou","chociaż","It's expensive, though I like it."),
    ("through","θruː","sru","przez","Walk through the park."),
    ("waste","weɪst","łejst","marnować / odpady","Don't waste your time on that."),
    ("wonder","ˈwʌndə","łandə","zastanawiać się","I wonder if he's coming."),
    ("worth","wɜːθ","łyrs","warty / warto","It's worth the effort."),
]

# Idiom pool (shared)
IDIOM_POOL = [
    ("hit the books","zabrać się do nauki","I have to hit the books — exam tomorrow."),
    ("piece of cake","bułka z masłem (łatwizna)","The test was a piece of cake."),
    ("under the weather","kiepsko się czuć","I'm under the weather today, I'll stay home."),
    ("break the ice","przełamać lody","She told a joke to break the ice."),
    ("call it a day","skończyć (pracę)","Let's call it a day, I'm exhausted."),
    ("cost an arm and a leg","kosztować majątek","That car cost an arm and a leg."),
    ("get the hang of","załapać (zrozumieć)","I'm finally getting the hang of this app."),
    ("on the same page","mieć to samo zdanie","Let's make sure we're on the same page."),
    ("the ball is in your court","ruch po twojej stronie","I've sent the offer — the ball is in your court."),
    ("burn the midnight oil","ślęczeć po nocy","She burned the midnight oil to finish the project."),
    ("cut corners","iść na skróty (oszczędzać kosztem jakości)","Don't cut corners on safety."),
    ("get cold feet","stchórzyć w ostatniej chwili","He got cold feet before the wedding."),
    ("hit the nail on the head","trafić w sedno","You hit the nail on the head with that idea."),
    ("once in a blue moon","raz na ruski rok","We only meet once in a blue moon."),
    ("pull someone's leg","nabijać się z kogoś","Relax, I'm just pulling your leg."),
    ("speak of the devil","o wilku mowa","Speak of the devil — there he is!"),
    ("the last straw","kropla, która przelała czarę","Being late again was the last straw."),
    ("a blessing in disguise","szczęście w nieszczęściu","Losing that job was a blessing in disguise."),
    ("beat around the bush","owijać w bawełnę","Stop beating around the bush — say it."),
    ("get out of hand","wymknąć się spod kontroli","The party got out of hand."),
    ("in hot water","w tarapatach","He's in hot water with his boss."),
    ("let the cat out of the bag","wygadać sekret","She let the cat out of the bag about the surprise."),
    ("on cloud nine","w siódmym niebie","She's on cloud nine since the promotion."),
    ("rain check","odłożyć coś na później","Can I take a rain check on dinner?"),
    ("run out of steam","stracić zapał / siły","I ran out of steam by 4 pm."),
    ("see eye to eye","zgadzać się z kimś","We don't always see eye to eye."),
    ("take it with a grain of salt","traktować z przymrużeniem oka","Take what he says with a grain of salt."),
    ("through thick and thin","na dobre i na złe","She stood by me through thick and thin."),
    ("tip of the iceberg","wierzchołek góry lodowej","This problem is just the tip of the iceberg."),
    ("when pigs fly","jak mi kaktus wyrośnie","He'll apologise when pigs fly."),
    ("a piece of advice","rada","Let me give you a piece of advice."),
    ("back to square one","wracać do punktu wyjścia","The plan failed — we're back to square one."),
    ("by the book","zgodnie z zasadami","She does everything by the book."),
    ("face the music","ponieść konsekwencje","You broke it — now face the music."),
    ("give it a shot","spróbować","Give it a shot, what do you have to lose?"),
    ("hang in there","trzymaj się","Hang in there, it'll get better."),
    ("in the long run","na dłuższą metę","It pays off in the long run."),
    ("keep an eye on","mieć oko na","Keep an eye on the kids for me."),
    ("make ends meet","wiązać koniec z końcem","It's hard to make ends meet these days."),
    ("out of the blue","ni stąd ni zowąd","She called me out of the blue."),
    ("read between the lines","czytać między wierszami","Read between the lines — he's unhappy."),
    ("spill the beans","wygadać tajemnicę","Come on, spill the beans!"),
    ("steal the show","skraść show","The kids stole the show at the wedding."),
    ("take with a pinch of salt","przyjmować z rezerwą","Take his promises with a pinch of salt."),
    ("up in the air","niepewne / wisi w powietrzu","Our holiday plans are up in the air."),
    ("walk on eggshells","stąpać po cienkim lodzie","I have to walk on eggshells around him."),
    ("wear many hats","pełnić wiele ról","In a small company you wear many hats."),
    ("worth its weight in gold","na wagę złota","A good mechanic is worth their weight in gold."),
    ("at the drop of a hat","bez zastanowienia","She'd help anyone at the drop of a hat."),
    ("bite the bullet","zacisnąć zęby","I bit the bullet and went to the dentist."),
]

# Grammar pool — extended explanations (B1/B2). Round-robin per lesson.
GRAMMAR_POOL = [
    ("Present Perfect vs Past Simple",
     "Present Perfect (have/has + III forma): doświadczenie życiowe (ever, never), czynność z efektem teraz (just, already, yet), czas nieokreślony, okres do teraz (for, since, recently).\nPast Simple (II forma / -ed): czynność ZAKOŃCZONA w określonym momencie przeszłości (yesterday, in 2018, last week, ago, when I was...).\nZłota zasada: z konkretnym czasem w przeszłości NIGDY nie używamy Present Perfect.",
     ["I have lived here for five years.", "I lived in Berlin in 2018.", "Have you ever tried sushi?", "She didn't call me yesterday."]),
    ("First & Second Conditional",
     "1st Conditional — realne sytuacje przyszłe: If + Present Simple, will/can/may + bezokolicznik. Po 'if' NIGDY 'will'.\n2nd Conditional — hipoteza nierealna/mało prawdopodobna: If + Past Simple, would/could/might + bezokolicznik. Dla 'be' używamy 'were' dla wszystkich osób (If I were you...).\nNie mieszaj typów w jednym zdaniu.",
     ["If it rains, I will stay home.", "If I were rich, I would travel more.", "If she calls, tell her I'm out.", "If I had more time, I would learn Spanish."]),
    ("Modal verbs: must / have to / should",
     "must — silna konieczność lub przekonanie mówiącego.\nhave to — obowiązek zewnętrzny (zasada, polecenie).\nshould — rada, sugestia, opinia.\nmustn't = ZAKAZ; don't have to = brak konieczności (te dwa znaczą co innego!).\nPo modalach NIE używamy 'to' (oprócz 'have to', 'ought to', 'be able to').",
     ["I must finish this today.", "I have to wear a uniform at work.", "You should see a doctor.", "You mustn't smoke here."]),
    ("Reported Speech",
     "Cofamy czasy o jeden krok: Present → Past, Past → Past Perfect, will → would, can → could, must → had to.\nZmieniamy zaimki (I → he/she) i okoliczniki: now → then, today → that day, tomorrow → the next day, yesterday → the day before.\nW pytaniach pośrednich: BRAK inwersji, BRAK do/does/did, używamy 'if/whether' (yes/no) lub słówka pytajnego.",
     ["He said, 'I'm tired.' → He said he was tired.", "She said, 'I will call.' → She said she would call.", "He said, 'I saw it.' → He said he had seen it.", "She asked where I lived."]),
    ("Passive Voice",
     "be + III forma. Używamy gdy ważniejsza jest czynność niż wykonawca, lub wykonawca jest nieznany/oczywisty.\nFormy: Present Simple — is/are made; Past Simple — was/were built; Present Perfect — has/have been done; Future — will be sent; Modal — must be checked; Continuous — is being repaired.\n'by' wprowadza wykonawcę.",
     ["The report is sent every Friday.", "This house was built in 1920.", "The package has been delivered.", "You will be informed by email."]),
    ("Used to / would for past habits",
     "used to + bezokolicznik — przeszły NAWYK lub STAN, którego już nie ma.\nwould + bezokolicznik — TYLKO powtarzające się czynności (nie stany!).\nPytanie/przeczenie: did/didn't USE to (bez 'd').\nNie myl: 'be used to + -ing' = być przyzwyczajonym.",
     ["I used to smoke, but I quit.", "We used to live in Warsaw.", "Every summer we would visit our grandparents.", "I didn't use to like coffee."]),
    ("Articles: a / an / the / —",
     "a/an — coś po raz pierwszy, jedno z wielu; 'an' przed dźwiękiem samogłoskowym (an hour, a university).\nthe — coś znane, jedyne (the sun), z superlatywami (the best), z instrumentami (the piano), z nazwami zawierającymi 'of' (the University of Warsaw).\nzero — pojęcia ogólne (Life is short), rzeczowniki mnogie ogólne (Cats love milk), nazwy własne (Poland), posiłki, 'go to work/school/bed'.",
     ["I bought a car. The car is red.", "She plays the piano.", "Cats love milk.", "He's an engineer."]),
    ("Gerunds and Infinitives",
     "Verb + -ing: enjoy, avoid, finish, mind, suggest, consider, recommend, can't stand, keep, practise, admit, deny, postpone.\nVerb + to + bezokolicznik: want, decide, plan, hope, agree, promise, refuse, manage, learn, offer, expect, afford.\nPo PRZYIMKACH zawsze -ing.\nZmiana znaczenia: 'stop to smoke' (przerwał, by zapalić) ≠ 'stop smoking' (rzucił palenie). Podobnie: remember, forget, try, regret.",
     ["I enjoy reading.", "She decided to leave.", "I'm interested in learning French.", "He stopped to smoke. (przerwał, by zapalić) vs He stopped smoking. (rzucił palenie)"]),
    ("Future forms: will / going to / Present Continuous",
     "will — decyzja w momencie mówienia, obietnica, przewidywanie BEZ dowodu.\nbe going to — plan/intencja, przewidywanie z DOWODEM teraz.\nPresent Continuous — ustalony plan z konkretnym czasem.\nPresent Simple — rozkład jazdy, harmonogram (The train leaves at 8).",
     ["I'll help you with that.", "I'm going to start a new course.", "I'm meeting Tom at 7.", "Look at the clouds — it's going to rain."]),
    ("Comparatives and Superlatives",
     "1 sylaba: -er/-est (tall→taller→tallest). Końcowa spółgłoska po samogłosce: podwajamy (big→bigger).\n2 syl. na -y: y→i+er/est (happy→happier).\n2+ syl.: more/most (more interesting).\nNieregularne: good→better→best, bad→worse→worst, far→further→furthest, much/many→more→most.\nKonstrukcje: 'as ... as', 'not as ... as', 'the + comparative, the + comparative' (im więcej tym...).",
     ["This task is easier than the last one.", "She is the most experienced in the team.", "My English is getting better and better.", "Today is worse than yesterday."]),
    ("Present Perfect Continuous",
     "have/has been + -ing. Czynność rozpoczęta w przeszłości i trwająca DO TERAZ (for/since) lub niedawno zakończona z widocznym skutkiem.\nTypowe markery: for, since, all day, lately, recently, how long.\nCzasowniki STANOWE (know, like, believe, own) używają Present Perfect SIMPLE, nie Continuous.",
     ["I have been learning English for two years.", "She has been working since 8 am.", "It's been raining all day.", "Why are you tired? — I've been running."]),
    ("Relative Clauses (who / which / that)",
     "who — osoby; which — rzeczy/zwierzęta; that — osoby i rzeczy (tylko w defining); whose — posiadanie; where — miejsce; when — czas.\nDefining (bez przecinków) — informacja KONIECZNA. Można pominąć who/which/that gdy jest dopełnieniem.\nNon-defining (w przecinkach) — informacja DODATKOWA; NIE używamy 'that', nie pomijamy zaimka.",
     ["The man who called you is here.", "The book which I bought is great.", "My brother, who lives in Paris, is a doctor.", "The car that broke down was old."]),
    ("Question tags",
     "Twierdzenie + przeczący tag; przeczenie + twierdzący tag. Powtarzamy operator (be/do/have/modal) + zaimek.\nBrak operatora w Present/Past Simple → do/does/did.\nWyjątki: I am → aren't I; Let's → shall we; imperative → will you / won't you; Somebody/Nobody → they.",
     ["You're coming, aren't you?", "He doesn't smoke, does he?", "She can drive, can't she?", "They've finished, haven't they?"]),
    ("So / Such / Too / Enough",
     "so + adj/adv (so cold, so quickly).\nsuch + (a/an) + (adj) + noun (such a kind person, such nice weather).\ntoo + adj = ZA bardzo (negatywne).\nadj + enough = WYSTARCZAJĄCO. enough + noun.\nKonstrukcje: too...to + inf., ...enough to + inf., so/such...that.",
     ["It's so cold today.", "She is such a kind person.", "This coffee is too hot.", "Are you old enough to vote?"]),
    ("Phrasal verbs in business",
     "look into = zbadać; carry out = przeprowadzić; put off = odłożyć; bring up = poruszyć temat; go through = przejrzeć; come up with = wymyślić; follow up (on) = nawiązać; back up = popierać / robić kopię; sort out = rozwiązać; turn down = odrzucić; set up = założyć; lay off = zwolnić (z pracy).\nSeparowalne (look it up) vs nieseparowalne (look into it).",
     ["I'll look into the issue.", "We carried out a survey.", "Let's put off the meeting.", "She came up with a great idea."]),
    ("Third Conditional",
     "If + Past Perfect (had + III), would/could/might have + III forma. Hipoteza dotycząca PRZESZŁOŚCI, której nie da się zmienić — często wyraża żal lub krytykę.\nPo 'if' NIGDY 'would have'.\nMixed Conditional: warunek przeszły, skutek teraz (If I had studied medicine, I would be a doctor now).",
     ["If I had studied, I would have passed.", "If she had called, I would have helped.", "If we hadn't taken a taxi, we would have missed the flight."]),
    ("Quantifiers: much / many / a few / a little",
     "much + niepoliczalne (głównie w pyt./przecz.); many + policzalne l.mn.; a lot of / lots of — neutralnie do obu.\na few + policzalne = kilka (pozytywne); few = mało (negatywne).\na little + niepoliczalne = trochę; little = mało (negatywne).",
     ["How much sugar do you take?", "I have many friends.", "There are a few biscuits left.", "We have little time."]),
    ("Wish + Past / Past Perfect",
     "I wish + Past Simple — żal o teraźniejszość (I wish I knew = szkoda, że nie wiem).\nI wish + Past Perfect — żal o przeszłość (I wish I had studied).\nI wish + would — irytujące zachowanie INNYCH (I wish you wouldn't interrupt). Nie używamy 'I wish I would'.\nDla 'be' po 'wish' → 'were' dla wszystkich osób.",
     ["I wish I knew the answer.", "I wish I had studied harder.", "I wish you wouldn't interrupt me.", "She wishes she had a bigger flat."]),
    ("Linking words: although / however / despite",
     "although / even though + ZDANIE.\nhowever = jednak — SAMODZIELNE, w przecinkach, łączy dwa zdania.\ndespite / in spite of + RZECZOWNIK lub -ing lub 'the fact that'.\nNIGDY: 'Despite it was raining'. Poprawnie: 'Despite the rain' / 'Although it was raining'.",
     ["Although it was cold, we walked.", "It was raining; however, we went out.", "Despite the rain, we walked.", "In spite of being tired, she finished the report."]),
    ("Indirect / Embedded questions",
     "Pytania pośrednie mają szyk TWIERDZĄCY (no inversion, no do/does/did).\nWprowadzamy: Could you tell me..., Do you know..., I wonder..., Have you any idea...\nYes/no → 'if' lub 'whether'.\nWh- → szyk twierdzący po słówku pytajnym.",
     ["Could you tell me where the station is?", "Do you know what time it starts?", "I wonder if she is coming.", "Can you tell me how this works?"]),
]

# Form tables (used by GrammarBlock) — list of (label, structure_or_example, extra).
GRAMMAR_FORMS = {
    "Present Perfect vs Past Simple": [
        ("+", "I have worked / She has worked", "I worked / She worked"),
        ("–", "I haven't worked / She hasn't worked", "I didn't work"),
        ("?", "Have you worked? / Has she worked?", "Did you work?"),
        ("markery", "for, since, ever, never, just, already, yet", "yesterday, ago, in 2018, last week"),
    ],
    "First & Second Conditional": [
        ("1st (+)", "If I have time, I will call.", ""),
        ("1st (–)", "If I don't have time, I won't call.", ""),
        ("2nd (+)", "If I had time, I would call.", ""),
        ("2nd (–)", "If I didn't have time, I wouldn't call.", ""),
        ("be → were", "If I were you, I would apologise.", ""),
    ],
    "Modal verbs: must / have to / should": [
        ("must (+)", "I must go now.", ""),
        ("must (–) = ZAKAZ", "You mustn't smoke here.", ""),
        ("have to (+)", "She has to wear a tie.", ""),
        ("have to (–) = brak konieczności", "You don't have to come.", ""),
        ("should", "You should rest. / You shouldn't worry.", ""),
    ],
    "Reported Speech": [
        ("Present → Past", "'I work' → He said he worked.", ""),
        ("Pres. Cont. → Past Cont.", "'I'm working' → He said he was working.", ""),
        ("Past → Past Perfect", "'I saw it' → He said he had seen it.", ""),
        ("will → would, can → could", "'I will help' → She said she would help.", ""),
        ("say vs tell", "He SAID that... / He TOLD me that...", ""),
    ],
    "Passive Voice": [
        ("Present Simple", "Reports are sent every Friday.", ""),
        ("Past Simple", "The house was built in 1920.", ""),
        ("Present Perfect", "The package has been delivered.", ""),
        ("Future", "You will be informed by email.", ""),
        ("Continuous", "My car is being repaired now.", ""),
        ("Modal", "This must be checked twice.", ""),
    ],
    "Used to / would for past habits": [
        ("used to (+)", "I used to smoke.", ""),
        ("used to (–)", "I didn't use to smoke.", ""),
        ("used to (?)", "Did you use to live here?", ""),
        ("would (powtarzane)", "Every summer we would visit grandparents.", ""),
        ("be used to + -ing", "I'm used to working late.", ""),
    ],
    "Articles: a / an / the / —": [
        ("a / an", "a car, an hour, a university", ""),
        ("the", "the sun, the best, the UK, the piano", ""),
        ("zero", "Cats love milk. Life is short.", ""),
        ("zawód", "She is a teacher. He's an engineer.", ""),
    ],
    "Gerunds and Infinitives": [
        ("verb + -ing", "enjoy, avoid, finish, mind, suggest, can't stand", ""),
        ("verb + to + inf.", "want, decide, plan, hope, agree, refuse, afford", ""),
        ("preposition + -ing", "interested in learning, good at cooking", ""),
        ("zmiana znaczenia", "stop to do ≠ stop doing; remember to do ≠ remember doing", ""),
    ],
    "Future forms: will / going to / Present Continuous": [
        ("will", "decyzja teraz / obietnica: I'll help you.", ""),
        ("be going to", "plan / przewidywanie z dowodu: It's going to rain.", ""),
        ("Present Continuous", "ustalony plan: I'm meeting Tom at 7.", ""),
        ("Present Simple", "rozkład: The train leaves at 8.", ""),
    ],
    "Comparatives and Superlatives": [
        ("1 syl. -er/-est", "tall → taller → the tallest", ""),
        ("2 syl. -y → -ier/-iest", "happy → happier → the happiest", ""),
        ("długie: more / most", "interesting → more interesting → the most interesting", ""),
        ("nieregularne", "good→better→best; bad→worse→worst; far→further→furthest", ""),
        ("równość", "as tall as / not as tall as", ""),
    ],
    "Present Perfect Continuous": [
        ("(+)", "I have been working / She has been working", ""),
        ("(–)", "I haven't been working", ""),
        ("(?)", "Have you been working?", ""),
        ("markery", "for, since, all day, lately, how long", ""),
        ("stanowe → Simple", "I have known him for years. (NIE: have been knowing)", ""),
    ],
    "Relative Clauses (who / which / that)": [
        ("who — osoby", "The woman who lives next door is a doctor.", ""),
        ("which — rzeczy", "The book which I bought is great.", ""),
        ("that — osoby/rzeczy (defining)", "The car that broke down was old.", ""),
        ("whose — posiadanie", "The man whose car was stolen called the police.", ""),
        ("non-defining", "My brother, who lives in Paris, is a doctor.", ""),
    ],
    "Question tags": [
        ("twierdz. → przecz.", "You're coming, aren't you?", ""),
        ("przecz. → twierdz.", "He doesn't smoke, does he?", ""),
        ("modal", "She can drive, can't she?", ""),
        ("I am → aren't I", "I'm late, aren't I?", ""),
        ("Let's → shall we", "Let's go, shall we?", ""),
    ],
    "So / Such / Too / Enough": [
        ("so + adj/adv", "It's so cold. She runs so fast.", ""),
        ("such + (a/an) + (adj) + noun", "She is such a kind person.", ""),
        ("too + adj (za bardzo)", "This coffee is too hot to drink.", ""),
        ("adj + enough (wystarczająco)", "She is old enough to vote.", ""),
        ("enough + noun", "We don't have enough time.", ""),
    ],
    "Phrasal verbs in business": [
        ("look into", "zbadać sprawę", ""),
        ("carry out", "przeprowadzić (plan, badanie)", ""),
        ("put off", "odłożyć w czasie", ""),
        ("come up with", "wymyślić (pomysł)", ""),
        ("turn down / lay off / set up / sort out", "odrzucić / zwolnić / założyć / rozwiązać", ""),
    ],
    "Third Conditional": [
        ("(+)", "If I had studied, I would have passed.", ""),
        ("(–)", "If she hadn't called, I wouldn't have known.", ""),
        ("(?)", "Would you have helped if I had asked?", ""),
        ("mixed", "If I had taken that job, I would be richer now.", ""),
    ],
    "Quantifiers: much / many / a few / a little": [
        ("much + niepoliczalne", "How much money? Not much time.", ""),
        ("many + policzalne", "How many people? Many friends.", ""),
        ("a few / few + policzalne", "a few biscuits (kilka) / few people (mało)", ""),
        ("a little / little + niepoliczalne", "a little milk (trochę) / little time (mało)", ""),
        ("neutralne", "a lot of / lots of — pasuje do obu", ""),
    ],
    "Wish + Past / Past Perfect": [
        ("wish + Past Simple", "I wish I knew the answer. (teraz)", ""),
        ("wish + Past Perfect", "I wish I had studied harder. (przeszłość)", ""),
        ("wish + would (inni)", "I wish you wouldn't interrupt me.", ""),
        ("be → were", "I wish I were taller.", ""),
    ],
    "Linking words: although / however / despite": [
        ("although + zdanie", "Although it rained, we went out.", ""),
        ("however + przecinki", "It was cold; however, we walked.", ""),
        ("despite / in spite of + noun/-ing", "Despite the rain / Despite being tired", ""),
        ("despite the fact that + zdanie", "Despite the fact that it rained, we walked.", ""),
    ],
    "Indirect / Embedded questions": [
        ("yes/no → if/whether", "Do you know if she is coming?", ""),
        ("wh- → szyk twierdzący", "Could you tell me where the station is?", ""),
        ("bez do/does/did", "Do you know what time it starts?", ""),
        ("typowe początki", "I wonder... / Could you tell me... / Do you know...", ""),
    ],
}

# Real grammar MCQs per topic (5-6 each).
GRAMMAR_QUIZ_POOL = {
    "Present Perfect vs Past Simple": [
        {"q": "I _____ him yesterday at the conference.", "options": ["have seen", "saw", "have been seeing", "had saw"], "correct": 1, "explain": "Z 'yesterday' (konkretny czas) → Past Simple."},
        {"q": "She _____ in London since 2019.", "options": ["lives", "lived", "has lived", "is living"], "correct": 2, "explain": "Z 'since' (od momentu do teraz) → Present Perfect."},
        {"q": "Have you ever _____ caviar?", "options": ["try", "tried", "tryed", "been trying"], "correct": 1, "explain": "Doświadczenie życiowe ('ever') + III forma."},
        {"q": "He _____ his keys this morning. Now he can't get in.", "options": ["lost", "has lost", "loses", "had lost"], "correct": 1, "explain": "Skutek widoczny TERAZ → Present Perfect."},
        {"q": "When I was a child, I _____ in Gdańsk.", "options": ["have lived", "live", "lived", "was living"], "correct": 2, "explain": "Zakończony okres ('when I was a child') → Past Simple."},
        {"q": "We _____ each other for ten years.", "options": ["know", "knew", "have known", "are knowing"], "correct": 2, "explain": "'for ten years' do teraz, czasownik stanowy → Present Perfect Simple."},
    ],
    "First & Second Conditional": [
        {"q": "If it _____ tomorrow, we'll cancel the picnic.", "options": ["will rain", "rains", "rained", "would rain"], "correct": 1, "explain": "1st Conditional: po 'if' Present Simple, NIE 'will'."},
        {"q": "If I _____ you, I would apologise.", "options": ["was", "am", "were", "would be"], "correct": 2, "explain": "2nd Conditional, 'be' → 'were' dla wszystkich osób."},
        {"q": "If she _____ harder, she would pass.", "options": ["studies", "studied", "will study", "would study"], "correct": 1, "explain": "2nd Conditional: po 'if' Past Simple."},
        {"q": "If I _____ more time, I would learn Spanish.", "options": ["have", "had", "would have", "will have"], "correct": 1, "explain": "2nd Conditional: 'If + Past Simple, would + bezokolicznik'."},
        {"q": "If he calls, I _____ him you're out.", "options": ["tell", "told", "would tell", "will tell"], "correct": 3, "explain": "1st Conditional: w zdaniu głównym 'will + bezokolicznik'."},
        {"q": "What would you do if you _____ the lottery?", "options": ["win", "won", "will win", "would win"], "correct": 1, "explain": "2nd Conditional: po 'if' Past Simple."},
    ],
    "Modal verbs: must / have to / should": [
        {"q": "You _____ smoke in the hospital. It's strictly forbidden.", "options": ["mustn't", "don't have to", "shouldn't", "can't to"], "correct": 0, "explain": "Zakaz = mustn't."},
        {"q": "It's Sunday — you _____ get up early.", "options": ["mustn't", "don't have to", "shouldn't to", "must not to"], "correct": 1, "explain": "Brak konieczności = don't have to."},
        {"q": "She _____ wear a uniform at work — it's company policy.", "options": ["must", "has to", "should", "ought"], "correct": 1, "explain": "Obowiązek zewnętrzny → 'have/has to'."},
        {"q": "You look pale. You _____ see a doctor.", "options": ["must to", "should", "have", "ought"], "correct": 1, "explain": "Rada → should (bez 'to')."},
        {"q": "I _____ finish this report tonight — the deadline is tomorrow.", "options": ["should", "must", "don't have to", "mustn't"], "correct": 1, "explain": "Silna konieczność → must."},
        {"q": "He _____ call her — they had an argument.", "options": ["should", "shouldn't", "mustn't to", "doesn't have"], "correct": 1, "explain": "Odradzanie → shouldn't."},
    ],
    "Reported Speech": [
        {"q": "He said, 'I am tired.' → He said he _____ tired.", "options": ["is", "was", "had been", "would be"], "correct": 1, "explain": "Present → Past Simple."},
        {"q": "She said, 'I will call you.' → She said she _____ me.", "options": ["will call", "calls", "would call", "called"], "correct": 2, "explain": "will → would."},
        {"q": "He told me, 'I saw it yesterday.' → He told me he _____ it the day before.", "options": ["saw", "had seen", "has seen", "would see"], "correct": 1, "explain": "Past Simple → Past Perfect."},
        {"q": "She asked, 'Where do you live?' → She asked where I _____.", "options": ["do live", "lived", "live", "did live"], "correct": 1, "explain": "Brak inwersji, brak 'do/does'."},
        {"q": "He said, 'I can swim.' → He said he _____ swim.", "options": ["can", "could", "would", "had"], "correct": 1, "explain": "can → could."},
        {"q": "She _____ me she would come.", "options": ["said", "told", "spoke", "talked"], "correct": 1, "explain": "'tell' + osoba (told me)."},
    ],
    "Passive Voice": [
        {"q": "The letter _____ by Tom last week.", "options": ["wrote", "was wrote", "was written", "has written"], "correct": 2, "explain": "Past Simple Passive: was/were + III forma."},
        {"q": "The package has already _____.", "options": ["delivered", "been delivered", "being delivered", "deliver"], "correct": 1, "explain": "Present Perfect Passive: has been + III forma."},
        {"q": "My car _____ at the moment.", "options": ["is repaired", "is being repaired", "repairs", "has repaired"], "correct": 1, "explain": "Present Continuous Passive: is being + III forma."},
        {"q": "You _____ by email tomorrow.", "options": ["inform", "will inform", "will be informed", "are informed"], "correct": 2, "explain": "Future Passive: will be + III forma."},
        {"q": "This house _____ in 1920.", "options": ["built", "is built", "was built", "has built"], "correct": 2, "explain": "Past Simple Passive."},
        {"q": "Safety rules _____ be checked every day.", "options": ["must", "must to", "must be", "have"], "correct": 2, "explain": "Modal Passive: modal + be + III forma."},
    ],
    "Used to / would for past habits": [
        {"q": "I _____ smoke, but I quit five years ago.", "options": ["use to", "used to", "would", "am used to"], "correct": 1, "explain": "Przeszły nawyk, którego już nie ma → 'used to'."},
        {"q": "Did you _____ live in Berlin?", "options": ["used to", "use to", "using to", "be used to"], "correct": 1, "explain": "Po 'did' wraca forma podstawowa 'use to'."},
        {"q": "We _____ live in Warsaw, but now we're in Kraków.", "options": ["would", "are used to", "used to", "use to"], "correct": 2, "explain": "STAN (live) → tylko 'used to', nie 'would'."},
        {"q": "I _____ working night shifts now — I've got used to it.", "options": ["used to", "am used to", "would", "use to"], "correct": 1, "explain": "'be used to + -ing' = być przyzwyczajonym."},
        {"q": "She _____ like coffee, but now she loves it.", "options": ["didn't use to", "didn't used to", "wouldn't", "isn't used to"], "correct": 0, "explain": "Przeczenie: 'didn't use to'."},
        {"q": "Every Friday my grandpa _____ tell us stories.", "options": ["use to", "is used to", "would", "uses"], "correct": 2, "explain": "Powtarzana czynność → 'would' lub 'used to'."},
    ],
    "Articles: a / an / the / —": [
        {"q": "I am _____ engineer at a software company.", "options": ["—", "a", "an", "the"], "correct": 2, "explain": "Samogłoska na początku → 'an'."},
        {"q": "She plays _____ piano beautifully.", "options": ["a", "—", "the", "an"], "correct": 2, "explain": "Instrumenty → 'the'."},
        {"q": "_____ life is full of surprises.", "options": ["The", "A", "—", "An"], "correct": 2, "explain": "Pojęcia ogólne → zero article."},
        {"q": "I bought a car. _____ car is red.", "options": ["A", "An", "The", "—"], "correct": 2, "explain": "Drugie wspomnienie — znane → 'the'."},
        {"q": "She studied at _____ University of Warsaw.", "options": ["—", "a", "an", "the"], "correct": 3, "explain": "Nazwy z 'of' → 'the'."},
        {"q": "We have breakfast and then go to _____ work.", "options": ["the", "a", "—", "an"], "correct": 2, "explain": "'go to work / school / bed' — bez rodzajnika."},
    ],
    "Gerunds and Infinitives": [
        {"q": "I enjoy _____ in the evenings.", "options": ["to read", "reading", "read", "to reading"], "correct": 1, "explain": "Po 'enjoy' zawsze -ing."},
        {"q": "She decided _____ the job.", "options": ["taking", "to take", "take", "to taking"], "correct": 1, "explain": "Po 'decide' + to + bezokolicznik."},
        {"q": "I'm interested in _____ French.", "options": ["learn", "to learn", "learning", "learned"], "correct": 2, "explain": "Po PRZYIMKU zawsze -ing."},
        {"q": "He stopped _____ a cigarette during the meeting.", "options": ["smoking", "to smoke", "smoke", "to smoking"], "correct": 1, "explain": "'stop to do' = przerwał, żeby zrobić."},
        {"q": "Would you mind _____ the window?", "options": ["to open", "open", "opening", "opened"], "correct": 2, "explain": "Po 'mind' -ing."},
        {"q": "We can't afford _____ a new car right now.", "options": ["buying", "to buy", "buy", "to buying"], "correct": 1, "explain": "Po 'afford' + to + bezokolicznik."},
    ],
    "Future forms: will / going to / Present Continuous": [
        {"q": "Look at those black clouds! It _____ rain.", "options": ["will", "is going to", "is raining", "rains"], "correct": 1, "explain": "Przewidywanie z DOWODEM → 'be going to'."},
        {"q": "The phone is ringing. — Don't worry, I _____ get it.", "options": ["am getting", "will", "'ll", "am going to"], "correct": 2, "explain": "Decyzja w momencie mówienia → 'will'."},
        {"q": "I _____ Tom at 7 pm tomorrow — we've booked the table.", "options": ["will meet", "meet", "am meeting", "will be met"], "correct": 2, "explain": "Ustalony plan z konkretnym czasem → Present Continuous."},
        {"q": "Next year I _____ a new course.", "options": ["start", "am going to start", "will starting", "starts"], "correct": 1, "explain": "Plan/intencja → 'be going to'."},
        {"q": "The train _____ at 8:15 — we'd better hurry.", "options": ["is leaving", "will leave", "leaves", "is going to leave"], "correct": 2, "explain": "Rozkład jazdy → Present Simple."},
        {"q": "I think it _____ a great party.", "options": ["is being", "is going to be", "will be", "is"], "correct": 2, "explain": "Opinia/przewidywanie po 'I think' → 'will'."},
    ],
    "Comparatives and Superlatives": [
        {"q": "This task is _____ than the last one.", "options": ["easier", "more easy", "easiest", "more easier"], "correct": 0, "explain": "easy → easier (y→i+er)."},
        {"q": "She is _____ person in the team.", "options": ["the most experienced", "most experienced", "the more experienced", "more experienced"], "correct": 0, "explain": "Superlative: 'the most + długi przymiotnik'."},
        {"q": "My English is getting _____.", "options": ["gooder", "more good", "better", "the best"], "correct": 2, "explain": "good → better → best."},
        {"q": "Today is _____ than yesterday.", "options": ["bad", "worst", "worse", "more bad"], "correct": 2, "explain": "bad → worse → worst."},
        {"q": "She is _____ tall _____ her brother.", "options": ["as / as", "so / as", "more / than", "as / than"], "correct": 0, "explain": "Równość: 'as ... as'."},
        {"q": "This is _____ film I've ever seen.", "options": ["most boring", "the more boring", "the most boring", "more boring than"], "correct": 2, "explain": "Superlative z 'the most'."},
    ],
    "Present Perfect Continuous": [
        {"q": "I _____ English for two years.", "options": ["learn", "am learning", "have learned", "have been learning"], "correct": 3, "explain": "Czynność trwająca od 2 lat → PPC."},
        {"q": "Why are you out of breath? — I _____.", "options": ["have run", "ran", "have been running", "am running"], "correct": 2, "explain": "Niedawno zakończone z widocznym skutkiem → PPC."},
        {"q": "She _____ him for years.", "options": ["has been knowing", "has known", "knows", "is knowing"], "correct": 1, "explain": "Stany (know) → Present Perfect SIMPLE."},
        {"q": "It _____ since this morning.", "options": ["rains", "has rained", "has been raining", "is raining"], "correct": 2, "explain": "'since' + trwająca → PPC."},
        {"q": "How long _____ here?", "options": ["are you waiting", "do you wait", "have you been waiting", "had you waited"], "correct": 2, "explain": "'How long' o trwającej → PPC."},
        {"q": "I _____ this book three times.", "options": ["have been reading", "have read", "am reading", "read"], "correct": 1, "explain": "ILOŚĆ powtórzeń → Present Perfect Simple."},
    ],
    "Relative Clauses (who / which / that)": [
        {"q": "The man _____ called you is waiting outside.", "options": ["which", "who", "whose", "what"], "correct": 1, "explain": "Osoby → 'who'."},
        {"q": "The book _____ I bought yesterday is fantastic.", "options": ["who", "whose", "which", "what"], "correct": 2, "explain": "Rzeczy → 'which' (lub 'that')."},
        {"q": "My brother, _____ lives in Paris, is a doctor.", "options": ["that", "which", "who", "whose"], "correct": 2, "explain": "Non-defining (przecinki) → nie 'that'."},
        {"q": "That's the woman _____ car was stolen.", "options": ["who", "whose", "which", "that"], "correct": 1, "explain": "Posiadanie → 'whose'."},
        {"q": "This is the hotel _____ we stayed last summer.", "options": ["which", "that", "where", "when"], "correct": 2, "explain": "Miejsce → 'where'."},
        {"q": "The film _____ we watched was boring.", "options": ["what", "which", "who", "whose"], "correct": 1, "explain": "'what' NIE jest zaimkiem względnym."},
    ],
    "Question tags": [
        {"q": "You're coming to the party, _____?", "options": ["isn't it", "aren't you", "don't you", "won't you"], "correct": 1, "explain": "be + you → aren't you."},
        {"q": "He doesn't smoke, _____?", "options": ["doesn't he", "isn't he", "does he", "is he"], "correct": 2, "explain": "Przeczenie → twierdzący tag."},
        {"q": "She can drive, _____?", "options": ["can she", "can't she", "doesn't she", "isn't she"], "correct": 1, "explain": "Powtarzamy modal."},
        {"q": "They've finished, _____?", "options": ["haven't they", "didn't they", "don't they", "aren't they"], "correct": 0, "explain": "Present Perfect → haven't they."},
        {"q": "I'm late, _____?", "options": ["amn't I", "aren't I", "am I not", "isn't I"], "correct": 1, "explain": "Wyjątek: I am → aren't I."},
        {"q": "Let's go for a walk, _____?", "options": ["will we", "shall we", "do we", "don't we"], "correct": 1, "explain": "Po 'Let's' tag = 'shall we'."},
    ],
    "So / Such / Too / Enough": [
        {"q": "She is _____ kind person.", "options": ["so", "such", "such a", "too"], "correct": 2, "explain": "Przed (przym.+) rzeczownik l.poj. → 'such a/an'."},
        {"q": "This coffee is _____ hot to drink.", "options": ["so", "such", "too", "enough"], "correct": 2, "explain": "'too + adj + to inf.'"},
        {"q": "Are you old _____ to vote?", "options": ["too", "so", "enough", "such"], "correct": 2, "explain": "'enough' PO przymiotniku."},
        {"q": "It was _____ cold that we stayed home.", "options": ["such", "so", "too much", "enough"], "correct": 1, "explain": "'so + adj + that'."},
        {"q": "We don't have _____ to finish the project.", "options": ["enough time", "time enough", "too time", "such time"], "correct": 0, "explain": "'enough' przed rzeczownikiem."},
        {"q": "She runs _____ fast that no one can catch her.", "options": ["such", "so", "too", "enough"], "correct": 1, "explain": "Przed przysłówkiem → 'so'."},
    ],
    "Phrasal verbs in business": [
        {"q": "I'll _____ this issue and get back to you.", "options": ["look at", "look into", "look for", "look up"], "correct": 1, "explain": "'look into' = zbadać."},
        {"q": "We had to _____ the meeting because the boss was sick.", "options": ["put on", "put off", "put up", "put down"], "correct": 1, "explain": "'put off' = odłożyć."},
        {"q": "She _____ a brilliant idea during the brainstorm.", "options": ["came across", "came up with", "came up", "came over"], "correct": 1, "explain": "'come up with' = wymyślić."},
        {"q": "They had to _____ 200 employees due to the crisis.", "options": ["lay off", "lay out", "lay down", "lie off"], "correct": 0, "explain": "'lay off' = zwolnić z pracy."},
        {"q": "Can you _____ this report before Friday?", "options": ["go through", "go on", "go in", "go after"], "correct": 0, "explain": "'go through' = przejrzeć."},
        {"q": "He _____ the job offer because of the low salary.", "options": ["turned on", "turned in", "turned down", "turned off"], "correct": 2, "explain": "'turn down' = odrzucić."},
    ],
    "Third Conditional": [
        {"q": "If I _____ harder, I would have passed.", "options": ["studied", "had studied", "would study", "have studied"], "correct": 1, "explain": "3rd Conditional: 'If + Past Perfect, would have + III'."},
        {"q": "She would have called if she _____ your number.", "options": ["had", "had had", "would have", "has had"], "correct": 1, "explain": "Past Perfect of 'have' → 'had had'."},
        {"q": "If we hadn't taken a taxi, we _____ the flight.", "options": ["would miss", "missed", "would have missed", "had missed"], "correct": 2, "explain": "Skutek przeszły → would have + III."},
        {"q": "If you _____ me, I would have helped you.", "options": ["asked", "would ask", "had asked", "have asked"], "correct": 2, "explain": "Po 'if' Past Perfect."},
        {"q": "If I had taken that job, I _____ rich now.", "options": ["would have been", "would be", "had been", "am"], "correct": 1, "explain": "Mixed Conditional: skutek teraz → 'would + bezokolicznik'."},
        {"q": "We _____ the train if we had run faster.", "options": ["would catch", "had caught", "would have caught", "caught"], "correct": 2, "explain": "Klasyczny 3rd Conditional."},
    ],
    "Quantifiers: much / many / a few / a little": [
        {"q": "How _____ sugar do you take in coffee?", "options": ["many", "much", "few", "little"], "correct": 1, "explain": "Sugar = niepoliczalne → 'much'."},
        {"q": "I have _____ friends in Berlin.", "options": ["much", "a little", "many", "little"], "correct": 2, "explain": "Friends = policzalne → 'many'."},
        {"q": "There are _____ biscuits left — would you like one?", "options": ["a few", "few", "a little", "little"], "correct": 0, "explain": "'a few' = kilka (pozytywne)."},
        {"q": "We have _____ time, so let's hurry.", "options": ["a little", "little", "few", "a few"], "correct": 1, "explain": "'little' (bez 'a') = mało."},
        {"q": "_____ people came to the meeting — only three.", "options": ["A few", "Few", "Little", "A little"], "correct": 1, "explain": "'Few' = mało."},
        {"q": "Could I have _____ milk in my tea?", "options": ["a few", "few", "a little", "many"], "correct": 2, "explain": "Milk = niepoliczalne → 'a little'."},
    ],
    "Wish + Past / Past Perfect": [
        {"q": "I wish I _____ the answer.", "options": ["know", "knew", "would know", "had known"], "correct": 1, "explain": "wish o teraźniejszości → Past Simple."},
        {"q": "I wish I _____ harder for that exam last year.", "options": ["studied", "had studied", "would study", "study"], "correct": 1, "explain": "wish o przeszłości → Past Perfect."},
        {"q": "I wish you _____ interrupting me all the time.", "options": ["stop", "stopped", "would stop", "had stopped"], "correct": 2, "explain": "Irytujące zachowanie innych → wish + would."},
        {"q": "I wish I _____ taller.", "options": ["am", "was", "were", "would be"], "correct": 2, "explain": "Po 'wish' dla 'be' → 'were' dla wszystkich."},
        {"q": "She wishes she _____ a bigger flat.", "options": ["has", "had", "would have", "had had"], "correct": 1, "explain": "wish o teraźniejszości → Past Simple."},
        {"q": "If only she _____ me earlier!", "options": ["told", "tells", "had told", "would tell"], "correct": 2, "explain": "Żal o przeszłość → Past Perfect."},
    ],
    "Linking words: although / however / despite": [
        {"q": "_____ it was raining, we went for a walk.", "options": ["Despite", "However", "Although", "In spite of"], "correct": 2, "explain": "'although' + zdanie."},
        {"q": "_____ the rain, we went for a walk.", "options": ["Although", "Even though", "Despite", "However"], "correct": 2, "explain": "'despite' + rzeczownik."},
        {"q": "It was cold; _____, we walked all afternoon.", "options": ["although", "despite", "however", "in spite"], "correct": 2, "explain": "'however' samodzielnie, w przecinkach."},
        {"q": "Despite _____ tired, she finished the report.", "options": ["she was", "being", "to be", "was"], "correct": 1, "explain": "'despite' + -ing."},
        {"q": "_____ the fact that he's young, he's very experienced.", "options": ["Although", "Despite", "However", "Even"], "correct": 1, "explain": "'despite the fact that' + zdanie."},
        {"q": "She came to work _____ being ill.", "options": ["although", "despite", "however", "even though"], "correct": 1, "explain": "Przed -ing → 'despite'."},
    ],
    "Indirect / Embedded questions": [
        {"q": "Could you tell me where _____?", "options": ["is the station", "the station is", "does the station is", "the station does be"], "correct": 1, "explain": "Pytanie pośrednie → szyk twierdzący."},
        {"q": "Do you know what time _____?", "options": ["does it start", "it starts", "is it start", "it does start"], "correct": 1, "explain": "Brak 'do/does'."},
        {"q": "I wonder _____ she is coming.", "options": ["that", "if", "is", "does"], "correct": 1, "explain": "Po 'wonder' przy yes/no → 'if/whether'."},
        {"q": "Can you tell me how _____?", "options": ["does this work", "this works", "this does work", "is this work"], "correct": 1, "explain": "Szyk twierdzący po wh-."},
        {"q": "Have you any idea why _____?", "options": ["did he leave", "he left", "he did leave", "left he"], "correct": 1, "explain": "Brak inwersji i 'did'."},
        {"q": "I'd like to know whether you _____ free tomorrow.", "options": ["are", "do be", "will being", "is"], "correct": 0, "explain": "Po 'whether' szyk twierdzący."},
    ],
}

TOPICS = [
    # (slug, title_pl, level, theme_keywords_for_core_vocab)
    ("small-talk", "Small talk z nieznajomymi", "B1"),
    ("job-interview", "Rozmowa kwalifikacyjna", "B2"),
    ("office-emails", "E-maile w pracy", "B1"),
    ("meetings", "Spotkania i telekonferencje", "B2"),
    ("doctors-visit", "Wizyta u lekarza", "B1"),
    ("at-the-airport", "Na lotnisku", "B1"),
    ("hotel", "Zameldowanie w hotelu", "B1"),
    ("renting-flat", "Wynajem mieszkania", "B2"),
    ("banking", "W banku", "B1"),
    ("shopping", "Zakupy i reklamacje", "B1"),
    ("restaurant", "W restauracji", "B1"),
    ("negotiations", "Negocjacje", "B2"),
    ("project-management", "Zarządzanie projektem", "B2"),
    ("remote-work", "Praca zdalna", "B1"),
    ("public-transport", "Komunikacja miejska", "B1"),
    ("family-life", "Życie rodzinne", "B1"),
    ("hobbies", "Hobby i wolny czas", "B1"),
    ("health-gym", "Zdrowie i siłownia", "B1"),
    ("weather", "Pogoda i pory roku", "B1"),
    ("tech-gadgets", "Technologia i gadżety", "B2"),
    ("social-media", "Media społecznościowe", "B1"),
    ("asking-for-help", "Prośby o pomoc", "B1"),
    ("giving-feedback", "Udzielanie feedbacku", "B2"),
    ("conflict-at-work", "Konflikt w pracy", "B2"),
    ("career-change", "Zmiana kariery", "B2"),
    ("cooking", "Gotowanie i przepisy", "B1"),
    ("eating-out", "Jedzenie na mieście", "B1"),
    ("holidays", "Święta i celebracje", "B1"),
    ("sport", "Sport i ćwiczenia", "B1"),
    ("reading", "Czytanie i książki", "B2"),
    ("movies", "Filmy i seriale", "B1"),
    ("music", "Muzyka", "B1"),
    ("travel-planning", "Planowanie podróży", "B1"),
    ("sightseeing", "Zwiedzanie", "B1"),
    ("driving-cars", "Jazda samochodem", "B1"),
    ("education", "Edukacja i kursy", "B2"),
    ("online-learning", "Nauka online", "B2"),
    ("salary-benefits", "Wynagrodzenie i benefity", "B2"),
    ("working-abroad", "Praca za granicą", "B2"),
    ("customer-service", "Obsługa klienta", "B1"),
    ("complaints", "Składanie reklamacji", "B2"),
    ("apologizing", "Przepraszanie", "B1"),
    ("appointments", "Umawianie spotkań", "B1"),
    ("neighbours", "Pogaduszki z sąsiadami", "B1"),
    ("pets", "Zwierzęta domowe", "B1"),
    ("environment", "Środowisko i ekologia", "B2"),
    ("news", "Wiadomości i wydarzenia", "B2"),
    ("personal-finance", "Finanse osobiste", "B2"),
    ("insurance", "Ubezpieczenia", "B2"),
    ("life-goals", "Cele życiowe i emerytura", "B2"),
]

# Per-topic core vocab (5 each) — handcrafted minimal seed
CORE = {
"small-talk": [
    ("weather","ˈweðə","łeðə","pogoda","The weather is lovely today."),
    ("weekend","ˈwiːkend","łiikend","weekend","How was your weekend?"),
    ("neighbour","ˈneɪbə","nejbə","sąsiad","She's my new neighbour."),
    ("chat","tʃæt","czat","pogawędka / rozmawiać","We had a nice chat at the bus stop."),
    ("hometown","ˈhəʊmtaʊn","houmtałn","rodzinne miasto","My hometown is small but quiet."),
    ("acquaintance","əˈkweɪntəns","akłejntens","znajomy","He's just an acquaintance, not a friend."),
    ("stranger","ˈstreɪndʒə","strejndżə","nieznajomy","I don't talk to strangers easily."),
    ("polite","pəˈlaɪt","polajt","uprzejmy","Be polite to the new colleague."),
    ("awkward","ˈɔːkwəd","ookłəd","niezręczny","There was an awkward silence."),
    ("small talk","ˌsmɔːlˈtɔːk","smool took","pogaduszki","I'm bad at small talk."),
],
"job-interview": [
    ("interview","ˈɪntəvjuː","intəwju","rozmowa kwalifikacyjna","I have an interview tomorrow."),
    ("candidate","ˈkændɪdət","kandydət","kandydat","She is a strong candidate."),
    ("CV / resume","siː viː","sij wij","życiorys","Send your CV by Friday."),
    ("strength","streŋθ","strenks","mocna strona","My biggest strength is teamwork."),
    ("weakness","ˈwiːknəs","łijknes","słabość","I'm working on my weakness."),
    ("salary expectation","ˈsæləri","saləri","oczekiwania finansowe","What are your salary expectations?"),
    ("notice period","ˈnəʊtɪs ˈpɪərɪəd","noutys piriəd","okres wypowiedzenia","I have a one-month notice period."),
    ("hire","ˈhaɪə","hajə","zatrudniać","We hired three people last month."),
    ("position","pəˈzɪʃn","pozyszn","stanowisko","I'm applying for the manager position."),
    ("background","ˈbækɡraʊnd","bekgrałnd","doświadczenie / tło","Tell me about your background."),
],
"office-emails": [
    ("attachment","əˈtætʃmənt","ataczment","załącznik","Please find the attachment."),
    ("recipient","rɪˈsɪpiənt","risypjent","odbiorca","Add me to the recipient list."),
    ("subject","ˈsʌbdʒɪkt","sabdżekt","temat (maila)","The subject is unclear."),
    ("CC","siː siː","sij sij","do wiadomości","Please CC my manager."),
    ("reply","rɪˈplaɪ","riplaj","odpowiadać","I will reply by tomorrow."),
    ("forward","ˈfɔːwəd","foowəd","przesyłać dalej","Could you forward me his email?"),
    ("deadline","ˈdedlaɪn","dedlajn","ostateczny termin","The deadline is Friday."),
    ("regards","rɪˈɡɑːdz","rigaadz","pozdrowienia","Best regards, Anna"),
    ("draft","drɑːft","draaft","szkic / robocza wersja","I'll send you a draft."),
    ("follow up","ˈfɒləʊ ʌp","foloł ap","kontynuacja / przypomnienie","Just a quick follow-up on my last email."),
],
"meetings": [
    ("agenda","əˈdʒendə","adżenda","plan spotkania","I'll send the agenda."),
    ("minutes","ˈmɪnɪts","minyts","protokół ze spotkania","Who is taking the minutes?"),
    ("attendee","əˌtenˈdiː","atendij","uczestnik","All attendees received the link."),
    ("postpone","pəˈspəʊn","postpoun","odłożyć","Let's postpone the meeting."),
    ("brainstorm","ˈbreɪnstɔːm","brejnstoom","burza mózgów","Let's brainstorm new ideas."),
    ("agenda item","əˈdʒendə ˈaɪtəm","adżenda ajtem","punkt porządku obrad","Move to the next agenda item."),
    ("decision-maker","dɪˈsɪʒn ˈmeɪkə","disyżn mejkə","osoba decyzyjna","She is the decision-maker."),
    ("call back","ˈkɔːl bæk","kool bek","oddzwonić","I'll call you back."),
    ("mute","mjuːt","mjut","wyciszyć","Please mute your mic."),
    ("share screen","ʃeə skriːn","szeə skriin","udostępnić ekran","Can you share your screen?"),
],
"doctors-visit": [
    ("appointment","əˈpɔɪntmənt","apojntment","wizyta / umówiony termin","I have a doctor's appointment."),
    ("symptom","ˈsɪmptəm","symptem","objaw","My main symptom is a headache."),
    ("prescription","prɪˈskrɪpʃn","priskripszn","recepta","The doctor gave me a prescription."),
    ("painkiller","ˈpeɪnkɪlə","pejnkylə","środek przeciwbólowy","I took a painkiller."),
    ("cough","kɒf","kof","kaszel / kasłać","I have a bad cough."),
    ("sore throat","sɔː θrəʊt","soo srout","ból gardła","I've got a sore throat."),
    ("blood pressure","blʌd ˈpreʃə","blad preszə","ciśnienie krwi","My blood pressure is normal."),
    ("dizzy","ˈdɪzi","dyzy","mający zawroty głowy","I feel dizzy."),
    ("rash","ræʃ","resz","wysypka","She has a rash on her arm."),
    ("get better","ɡet ˈbetə","get betə","wyzdrowieć","I hope you get better soon."),
],
"at-the-airport": [
    ("boarding pass","ˈbɔːdɪŋ pɑːs","boodyng paas","karta pokładowa","Show your boarding pass."),
    ("gate","ɡeɪt","gejt","bramka","The gate is closing."),
    ("luggage","ˈlʌɡɪdʒ","lagydż","bagaż","My luggage is missing."),
    ("delayed","dɪˈleɪd","dilejd","opóźniony","The flight is delayed."),
    ("check-in","ˈtʃek ɪn","czekin","odprawa","Check-in opens at 6."),
    ("security","sɪˈkjʊərəti","sikjurəti","kontrola bezpieczeństwa","Security took 30 minutes."),
    ("customs","ˈkʌstəmz","kastemz","odprawa celna","Go through customs after baggage claim."),
    ("layover","ˈleɪəʊvə","lejouwə","przesiadka","I have a 3-hour layover."),
    ("departure","dɪˈpɑːtʃə","dipaaczə","odlot","Departure is at 9 pm."),
    ("arrival","əˈraɪvl","arajwl","przylot","Arrival hall is downstairs."),
],
"hotel": [
    ("reception","rɪˈsepʃn","risepszn","recepcja","Ask at reception."),
    ("booking","ˈbʊkɪŋ","bukyng","rezerwacja","I have a booking under Smith."),
    ("double room","ˈdʌbl ruːm","dabl ruum","pokój dwuosobowy","I'd like a double room."),
    ("check out","tʃek aʊt","czek ałt","wymeldować się","Check-out is by 11."),
    ("amenities","əˈmenətiz","amenytyz","udogodnienia","The hotel has great amenities."),
    ("complimentary","ˌkɒmplɪˈmentri","komplymentry","gratis","Breakfast is complimentary."),
    ("Wi-Fi password","ˈwaɪfaɪ ˈpɑːswɜːd","łajfaj paasłyrd","hasło do Wi-Fi","What's the Wi-Fi password?"),
    ("housekeeping","ˈhaʊskiːpɪŋ","hałskijpyng","obsługa pokoju","Housekeeping comes at 10."),
    ("vacancy","ˈveɪkənsi","wejkənsi","wolny pokój","Sorry, no vacancies tonight."),
    ("front desk","frʌnt desk","frant desk","recepcja (US)","Leave the keys at the front desk."),
],
"renting-flat": [
    ("landlord","ˈlændlɔːd","lendloord","właściciel mieszkania","My landlord is very kind."),
    ("tenant","ˈtenənt","tenent","najemca","The new tenant moves in tomorrow."),
    ("lease","liːs","lijs","umowa najmu","I signed a one-year lease."),
    ("deposit","dɪˈpɒzɪt","dipozyt","kaucja","The deposit is two months' rent."),
    ("rent","rent","rent","czynsz / wynajmować","I pay the rent on the 1st."),
    ("utilities","juːˈtɪlətiz","jutyletyz","media (prąd, woda)","Utilities are not included."),
    ("furnished","ˈfɜːnɪʃt","fyrnyszt","umeblowany","The flat is fully furnished."),
    ("notice","ˈnəʊtɪs","noutys","wypowiedzenie","Give one month's notice."),
    ("viewing","ˈvjuːɪŋ","wjuyng","oglądanie mieszkania","Can we book a viewing?"),
    ("estate agent","ɪˈsteɪt ˈeɪdʒənt","estejt ejdżent","agent nieruchomości","The estate agent will call you."),
],
"banking": [
    ("account","əˈkaʊnt","akałnt","konto","I opened a new account."),
    ("transfer","ˈtrænsfɜː","transfyr","przelew","I made a transfer yesterday."),
    ("balance","ˈbæləns","belens","saldo","Check your balance online."),
    ("loan","ləʊn","loun","pożyczka","I took a loan for the car."),
    ("withdraw","wɪðˈdrɔː","łyzdroo","wypłacić (z konta)","I withdrew 200 zł."),
    ("deposit","dɪˈpɒzɪt","dipozyt","wpłata","Make a deposit at the ATM."),
    ("statement","ˈsteɪtmənt","stejtment","wyciąg","I got my monthly statement."),
    ("interest rate","ˈɪntrəst reɪt","intrest rejt","oprocentowanie","The interest rate went up."),
    ("overdraft","ˈəʊvədrɑːft","ouwədraaft","debet","I went into overdraft."),
    ("card","kɑːd","kaad","karta","I lost my card."),
],
"shopping": [
    ("receipt","rɪˈsiːt","risiit","paragon","Keep the receipt."),
    ("refund","ˈriːfʌnd","ryfand","zwrot pieniędzy","Can I get a refund?"),
    ("exchange","ɪksˈtʃeɪndʒ","ekscejndż","wymiana","I'd like to exchange this."),
    ("discount","ˈdɪskaʊnt","dyskałnt","zniżka","Is there a discount?"),
    ("size","saɪz","sajz","rozmiar","Do you have it in my size?"),
    ("try on","traɪ ɒn","traj on","przymierzyć","Can I try this on?"),
    ("checkout","ˈtʃekaʊt","czekałt","kasa","The checkout line is long."),
    ("on sale","ɒn seɪl","on sejl","na wyprzedaży","These shoes are on sale."),
    ("brand","brænd","brend","marka","I like this brand."),
    ("warranty","ˈwɒrənti","łoronty","gwarancja","It has a 2-year warranty."),
],
"restaurant": [
    ("menu","ˈmenjuː","menju","menu","Could I see the menu?"),
    ("starter","ˈstɑːtə","staatə","przystawka","I'll have a starter."),
    ("main course","meɪn kɔːs","mejn koos","danie główne","What's the main course?"),
    ("dessert","dɪˈzɜːt","dizyrt","deser","Skip the dessert today."),
    ("bill","bɪl","byl","rachunek","Could we have the bill?"),
    ("tip","tɪp","typ","napiwek","Leave a 10% tip."),
    ("reservation","ˌrezəˈveɪʃn","rezewejszn","rezerwacja","I have a reservation for 8."),
    ("waiter","ˈweɪtə","łejtə","kelner","The waiter was friendly."),
    ("vegetarian","ˌvedʒəˈteəriən","wedżeterjen","wegetariański","Do you have vegetarian options?"),
    ("allergy","ˈælədʒi","alerdży","alergia","I have a nut allergy."),
],
"negotiations": [
    ("offer","ˈɒfə","ofə","oferta","That's a good offer."),
    ("counter-offer","ˈkaʊntə ˈɒfə","kałntə ofə","kontroferta","Let me make a counter-offer."),
    ("compromise","ˈkɒmprəmaɪz","kompromajz","kompromis","We need a compromise."),
    ("bargain","ˈbɑːɡɪn","baagyn","targować się / okazja","She loves to bargain."),
    ("deal","diːl","dijl","umowa","It's a deal."),
    ("walk away","wɔːk əˈweɪ","łook ałej","odejść (od stołu)","Be ready to walk away."),
    ("leverage","ˈliːvərɪdʒ","liwerydż","przewaga / dźwignia","We have leverage here."),
    ("concede","kənˈsiːd","konsiid","ustąpić","I won't concede on price."),
    ("terms","tɜːmz","tyrmz","warunki","Let's review the terms."),
    ("win-win","ˌwɪnˈwɪn","łyn łyn","obustronnie korzystne","Aim for a win-win."),
],
"project-management": [
    ("scope","skəʊp","skoup","zakres projektu","Define the scope clearly."),
    ("milestone","ˈmaɪlstəʊn","majlstoun","kamień milowy","We hit a key milestone."),
    ("stakeholder","ˈsteɪkhəʊldə","stejkhoułdə","interesariusz","Update all stakeholders."),
    ("deliverable","dɪˈlɪvərəbl","diliwərebl","produkt / efekt","Send the deliverables on Friday."),
    ("backlog","ˈbæklɒɡ","beklog","zaległości / lista zadań","Our backlog is growing."),
    ("sprint","sprɪnt","sprynt","sprint (agile)","The sprint ends Tuesday."),
    ("budget","ˈbʌdʒɪt","badżyt","budżet","We're over budget."),
    ("risk","rɪsk","rysk","ryzyko","Identify the main risks."),
    ("scope creep","skəʊp kriːp","skoup kriip","rozrastanie zakresu","Watch out for scope creep."),
    ("kick-off","ˈkɪk ɒf","kyk of","spotkanie startowe","The kick-off is Monday."),
],
"remote-work": [
    ("remote","rɪˈməʊt","rimout","zdalny","I work remote."),
    ("commute","kəˈmjuːt","komjut","dojazd / dojeżdżać","No commute is the best perk."),
    ("schedule","ˈʃedjuːl","szedjul","harmonogram","My schedule is flexible."),
    ("home office","həʊm ˈɒfɪs","houm ofys","biuro domowe","Set up your home office well."),
    ("burnout","ˈbɜːnaʊt","byrnałt","wypalenie","Watch out for burnout."),
    ("VPN","viː piː en","wi pi en","sieć VPN","Connect to the VPN first."),
    ("hybrid","ˈhaɪbrɪd","hajbryd","hybrydowy","We work hybrid: 3+2."),
    ("standup","ˈstændʌp","stendap","krótkie spotkanie","Standup is at 9:30."),
    ("Slack","slæk","slek","komunikator (np. Slack)","Ping me on Slack."),
    ("async","eɪˈsɪŋk","ejsynk","asynchroniczny","We prefer async communication."),
],
"public-transport": [
    ("ticket","ˈtɪkɪt","tykyt","bilet","Buy a single ticket."),
    ("platform","ˈplætfɔːm","pletfoom","peron","The train leaves from platform 4."),
    ("station","ˈsteɪʃn","stejszn","stacja","Get off at the next station."),
    ("delay","dɪˈleɪ","dilej","opóźnienie","There's a 10-minute delay."),
    ("transfer","ˈtrænsfɜː","transfyr","przesiadka","You have to transfer at Central."),
    ("timetable","ˈtaɪmteɪbl","tajmtejbl","rozkład jazdy","Check the timetable online."),
    ("rush hour","rʌʃ ˈaʊə","rasz ałə","godziny szczytu","Avoid rush hour."),
    ("commuter","kəˈmjuːtə","komjutə","dojeżdżający","I'm a daily commuter."),
    ("fare","feə","feə","opłata za przejazd","The fare is 4 zł."),
    ("season ticket","ˈsiːzn ˈtɪkɪt","sijzn tykyt","bilet okresowy","I bought a monthly season ticket."),
],
"family-life": [
    ("relative","ˈrelətɪv","reletyw","krewny","I have relatives in Canada."),
    ("in-laws","ˈɪn lɔːz","in looz","teściowie","I get on well with my in-laws."),
    ("sibling","ˈsɪblɪŋ","syblyng","rodzeństwo","Do you have siblings?"),
    ("raise","reɪz","rejz","wychowywać","They raise their kids in two languages."),
    ("get along","ɡet əˈlɒŋ","get along","dogadywać się","We get along well."),
    ("toddler","ˈtɒdlə","todlə","małe dziecko","Our toddler is two."),
    ("teenager","ˈtiːneɪdʒə","tijnejdżə","nastolatek","Teenagers can be difficult."),
    ("housework","ˈhaʊswɜːk","hałsłyrk","prace domowe","We share the housework."),
    ("argue","ˈɑːɡjuː","aagju","kłócić się","Siblings argue a lot."),
    ("close","kləʊs","klous","bliski (emocjonalnie)","We're a close family."),
],
"hobbies": [
    ("hobby","ˈhɒbi","hoby","hobby","My hobby is photography."),
    ("painting","ˈpeɪntɪŋ","pejntyng","malowanie","She enjoys painting."),
    ("hiking","ˈhaɪkɪŋ","hajkyng","wędrówki","We go hiking on weekends."),
    ("gardening","ˈɡɑːdnɪŋ","gaadnyng","ogrodnictwo","Gardening is relaxing."),
    ("collect","kəˈlekt","kolekt","kolekcjonować","He collects vinyl records."),
    ("knitting","ˈnɪtɪŋ","nytyng","robienie na drutach","Knitting is back in fashion."),
    ("amateur","ˈæmətə","ametə","amator","I'm an amateur baker."),
    ("free time","friː taɪm","frij tajm","wolny czas","What do you do in your free time?"),
    ("passion","ˈpæʃn","peszn","pasja","Music is my passion."),
    ("relax","rɪˈlæks","ryleks","odpoczywać","I relax by reading."),
],
"health-gym": [
    ("workout","ˈwɜːkaʊt","łyrkałt","trening","I do a 30-minute workout."),
    ("treadmill","ˈtredmɪl","tredmyl","bieżnia","I ran on the treadmill."),
    ("weights","weɪts","łejts","ciężary","She lifts weights three times a week."),
    ("cardio","ˈkɑːdiəʊ","kaadjou","cardio","Cardio is essential."),
    ("trainer","ˈtreɪnə","trejnə","trener","I have a personal trainer."),
    ("stretch","stretʃ","strecz","rozciągać się","Stretch before running."),
    ("muscle","ˈmʌsl","masl","mięsień","My muscles are sore."),
    ("diet","ˈdaɪət","dajet","dieta","I'm on a low-carb diet."),
    ("calorie","ˈkæləri","keləry","kaloria","Count your calories."),
    ("rest day","rest deɪ","rest dej","dzień przerwy","Sunday is my rest day."),
],
"weather": [
    ("forecast","ˈfɔːkɑːst","fookaast","prognoza","Check the forecast."),
    ("shower","ˈʃaʊə","szałə","krótki deszcz","Just a quick shower."),
    ("freezing","ˈfriːzɪŋ","frijzyng","mróz / lodowato","It's freezing outside!"),
    ("humid","ˈhjuːmɪd","hjumyd","wilgotny","The air is humid."),
    ("breeze","briːz","briiz","wiaterek","A nice breeze."),
    ("thunderstorm","ˈθʌndəstɔːm","sandestoom","burza","There's a thunderstorm tonight."),
    ("blizzard","ˈblɪzəd","blizəd","zamieć śnieżna","The blizzard closed the roads."),
    ("heatwave","ˈhiːtweɪv","hijtłejw","fala upałów","A heatwave is coming."),
    ("drizzle","ˈdrɪzl","dryzl","mżawka","It's drizzling."),
    ("clear sky","klɪə skaɪ","kliə skaj","czyste niebo","A clear sky today."),
],
"tech-gadgets": [
    ("device","dɪˈvaɪs","diwajs","urządzenie","I bought a new device."),
    ("update","ˈʌpdeɪt","apdejt","aktualizacja","Run a software update."),
    ("battery","ˈbætri","betry","bateria","My battery is dead."),
    ("charger","ˈtʃɑːdʒə","czaadżə","ładowarka","Bring your charger."),
    ("wireless","ˈwaɪələs","łajeles","bezprzewodowy","Use wireless headphones."),
    ("backup","ˈbækʌp","bekap","kopia zapasowa","Make a backup."),
    ("cloud","klaʊd","klałd","chmura","I store files in the cloud."),
    ("setting","ˈsetɪŋ","setyng","ustawienie","Change the privacy settings."),
    ("software","ˈsɒftweə","softłeə","oprogramowanie","Update your software."),
    ("crash","kræʃ","kresz","awaria / zawiesić się","The app keeps crashing."),
],
"social-media": [
    ("post","pəʊst","poust","wpis / publikować","I'll post a photo."),
    ("follower","ˈfɒləʊə","folouwə","obserwujący","She has 10k followers."),
    ("like","laɪk","lajk","polubienie","Give it a like."),
    ("comment","ˈkɒment","koment","komentarz","Read the comments."),
    ("share","ʃeə","szeə","udostępnić","Share this with your friends."),
    ("scroll","skrəʊl","skroul","przewijać","I scroll for hours."),
    ("influencer","ˈɪnfluənsə","influensə","influencer","She's a fitness influencer."),
    ("hashtag","ˈhæʃtæɡ","hesztag","hashtag","Use the right hashtag."),
    ("notification","ˌnəʊtɪfɪˈkeɪʃn","noutyfikejszn","powiadomienie","Turn off notifications."),
    ("profile","ˈprəʊfaɪl","proufajl","profil","Update your profile."),
],
"asking-for-help": [
    ("favour","ˈfeɪvə","fejwə","przysługa","Can I ask a favour?"),
    ("urgent","ˈɜːdʒənt","yrdżent","pilny","This is urgent."),
    ("assist","əˈsɪst","asyst","pomagać","Can you assist me?"),
    ("guide","ɡaɪd","gajd","przewodnik / prowadzić","Can you guide me through it?"),
    ("manual","ˈmænjuəl","menjuəl","instrukcja","Check the manual."),
    ("clarify","ˈklærɪfaɪ","klaryfaj","wyjaśniać","Could you clarify that?"),
    ("hint","hɪnt","hynt","wskazówka","Give me a hint."),
    ("rescue","ˈreskjuː","reskju","ratować","You saved me — thank you for the rescue."),
    ("emergency","ɪˈmɜːdʒənsi","imyrdżensi","sytuacja awaryjna","Call me in an emergency."),
    ("kind","kaɪnd","kajnd","miły / uprzejmy","That's very kind of you."),
],
"giving-feedback": [
    ("feedback","ˈfiːdbæk","fijdbek","informacja zwrotna","I'd like some feedback."),
    ("praise","preɪz","prejz","pochwała","Praise the team often."),
    ("criticism","ˈkrɪtɪsɪzm","krytysyzm","krytyka","Constructive criticism helps."),
    ("improve","ɪmˈpruːv","impruuw","poprawiać","How can we improve?"),
    ("specific","spəˈsɪfɪk","spesyfyk","konkretny","Be specific in your feedback."),
    ("honest","ˈɒnɪst","onyst","szczery","Be honest with me."),
    ("appreciate","əˈpriːʃieɪt","apriszijejt","doceniać","I appreciate your effort."),
    ("performance","pəˈfɔːməns","pəfoomens","wyniki / praca","Your performance is great."),
    ("review","rɪˈvjuː","riwju","ocena / przegląd","Annual review is in May."),
    ("growth","ɡrəʊθ","grouts","rozwój","I see real growth in you."),
],
"conflict-at-work": [
    ("conflict","ˈkɒnflɪkt","konflykt","konflikt","Avoid open conflict."),
    ("misunderstanding","ˌmɪsʌndəˈstændɪŋ","mysandəstendyng","nieporozumienie","It was a misunderstanding."),
    ("HR","eɪtʃ ɑː","ejcz ar","dział kadr","Talk to HR."),
    ("colleague","ˈkɒliːɡ","kolijg","kolega z pracy","My colleague is upset."),
    ("complain","kəmˈpleɪn","kompleejn","skarżyć się","He complained to the boss."),
    ("mediate","ˈmiːdieɪt","miidiejt","mediować","I'll mediate between them."),
    ("apologise","əˈpɒlədʒaɪz","apolodżajz","przepraszać","He apologised quickly."),
    ("tension","ˈtenʃn","tenszn","napięcie","There's tension in the team."),
    ("calm down","kɑːm daʊn","kaam dałn","uspokoić się","Calm down and let's talk."),
    ("solve","sɒlv","solw","rozwiązać","Let's solve this together."),
],
"career-change": [
    ("career","kəˈrɪə","kariə","kariera","I want to change my career."),
    ("retrain","riːˈtreɪn","ritrejn","przekwalifikować się","I'll retrain as a coder."),
    ("opportunity","ˌɒpəˈtjuːnəti","opətjuunyti","okazja","A new opportunity came up."),
    ("network","ˈnetwɜːk","netłyrk","sieć kontaktów / nawiązywać kontakty","Build your network."),
    ("mentor","ˈmentɔː","mentoor","mentor","I found a great mentor."),
    ("skillset","ˈskɪlset","skylset","zestaw umiejętności","Expand your skillset."),
    ("transition","trænˈzɪʃn","tranzyszn","przejście / zmiana","Career transition takes time."),
    ("freelance","ˈfriːlɑːns","frijlaans","frilanser / wolny strzelec","I went freelance last year."),
    ("startup","ˈstɑːtʌp","staatap","startup","I joined a startup."),
    ("promotion","prəˈməʊʃn","promouszn","awans","She got a promotion."),
],
"cooking": [
    ("recipe","ˈresəpi","resepy","przepis","I followed the recipe."),
    ("ingredient","ɪnˈɡriːdiənt","ingrijdjent","składnik","Add the last ingredient."),
    ("chop","tʃɒp","czop","kroić","Chop the onions."),
    ("boil","bɔɪl","bojl","gotować","Boil the water."),
    ("fry","fraɪ","fraj","smażyć","Fry the eggs."),
    ("bake","beɪk","bejk","piec","Bake for 30 minutes."),
    ("oven","ˈʌvn","awn","piekarnik","Preheat the oven."),
    ("pan","pæn","pen","patelnia","Use a non-stick pan."),
    ("seasoning","ˈsiːzənɪŋ","sijzonyng","przyprawa","Add seasoning to taste."),
    ("leftovers","ˈleftəʊvəz","leftouwəz","resztki","I'll eat the leftovers tomorrow."),
],
"eating-out": [
    ("takeaway","ˈteɪkəweɪ","tejkəłej","jedzenie na wynos","Let's get a takeaway."),
    ("delivery","dɪˈlɪvəri","diliwery","dostawa","Free delivery on orders over 50."),
    ("brunch","brʌntʃ","brancz","brunch","We had brunch at noon."),
    ("buffet","ˈbʊfeɪ","bufej","bufet","All-you-can-eat buffet."),
    ("cuisine","kwɪˈziːn","kłyzyn","kuchnia (kulinarna)","I love Italian cuisine."),
    ("course","kɔːs","koos","danie","A three-course meal."),
    ("split the bill","splɪt ðə bɪl","splyt də byl","podzielić rachunek","Let's split the bill."),
    ("foodie","ˈfuːdi","fuudy","smakosz","She's a real foodie."),
    ("specials","ˈspeʃəlz","speszelz","dania dnia","Ask about the specials."),
    ("portion","ˈpɔːʃn","pooszn","porcja","The portion is huge."),
],
"holidays": [
    ("celebrate","ˈselɪbreɪt","selybrejt","świętować","We celebrated her birthday."),
    ("gift","ɡɪft","gyft","prezent","I bought a small gift."),
    ("decoration","ˌdekəˈreɪʃn","dekorejszn","dekoracja","Beautiful decorations."),
    ("tradition","trəˈdɪʃn","tradyszn","tradycja","It's a family tradition."),
    ("anniversary","ˌænɪˈvɜːsəri","anywyrseri","rocznica","Our 10th anniversary."),
    ("guest","ɡest","gest","gość","We have guests tonight."),
    ("host","həʊst","houst","gospodarz","I'll host this year."),
    ("toast","təʊst","toust","toast","Let's make a toast."),
    ("greeting","ˈɡriːtɪŋ","grijtyng","powitanie / życzenia","Send seasonal greetings."),
    ("invitation","ˌɪnvɪˈteɪʃn","inwytejszn","zaproszenie","Thanks for the invitation."),
],
"sport": [
    ("match","mætʃ","mecz","mecz","The match starts at 8."),
    ("score","skɔː","skoo","wynik / strzelić gola","What's the score?"),
    ("team","tiːm","tijm","drużyna","I play for the local team."),
    ("coach","kəʊtʃ","koucz","trener","Our coach is strict."),
    ("league","liːɡ","lijg","liga","Top of the league."),
    ("opponent","əˈpəʊnənt","oponent","przeciwnik","A tough opponent."),
    ("referee","ˌrefəˈriː","referi","sędzia","The referee made a mistake."),
    ("training","ˈtreɪnɪŋ","trejnyng","trening","Training is at 6."),
    ("injury","ˈɪndʒəri","indżery","kontuzja","He's out with an injury."),
    ("fan","fæn","fen","kibic","A huge football fan."),
],
"reading": [
    ("novel","ˈnɒvl","nowl","powieść","I read a great novel."),
    ("author","ˈɔːθə","oosə","autor","Who's the author?"),
    ("chapter","ˈtʃæptə","czeptə","rozdział","Finish this chapter."),
    ("plot","plɒt","plot","fabuła","The plot is complex."),
    ("character","ˈkærəktə","kerektə","postać","I love the main character."),
    ("genre","ˈʒɒnrə","żonrə","gatunek","Sci-fi is my favourite genre."),
    ("fiction","ˈfɪkʃn","fykszn","fikcja","I prefer fiction."),
    ("biography","baɪˈɒɡrəfi","bajogrəfi","biografia","I'm reading a biography."),
    ("bookshelf","ˈbʊkʃelf","bukszelf","półka na książki","My bookshelf is full."),
    ("audiobook","ˈɔːdiəʊbʊk","oodiouubuk","audiobook","I listen to audiobooks while driving."),
],
"movies": [
    ("scene","siːn","sijn","scena","My favourite scene."),
    ("director","dəˈrektə","dyrektə","reżyser","The director won an Oscar."),
    ("actor","ˈæktə","ektə","aktor","Great cast of actors."),
    ("subtitles","ˈsʌbtaɪtlz","sabtajtlz","napisy","Turn on the subtitles."),
    ("plot twist","plɒt twɪst","plot tłyst","zwrot akcji","I didn't see that plot twist!"),
    ("episode","ˈepɪsəʊd","epysout","odcinek","One more episode."),
    ("season","ˈsiːzn","sijzn","sezon","Season three is the best."),
    ("trailer","ˈtreɪlə","trejlə","zwiastun","The trailer looks great."),
    ("spoiler","ˈspɔɪlə","spojlə","spoiler","No spoilers, please!"),
    ("binge-watch","bɪndʒ wɒtʃ","bindż łocz","oglądać kilka odcinków pod rząd","We binge-watched it in a weekend."),
],
"music": [
    ("song","sɒŋ","song","piosenka","I love this song."),
    ("band","bænd","bend","zespół","My favourite band."),
    ("album","ˈælbəm","elbem","album","New album dropped today."),
    ("concert","ˈkɒnsət","konsət","koncert","The concert was amazing."),
    ("lyrics","ˈlɪrɪks","lyryks","tekst piosenki","The lyrics are deep."),
    ("playlist","ˈpleɪlɪst","plejlyst","playlista","Make a workout playlist."),
    ("headphones","ˈhedfəʊnz","hedfounz","słuchawki","I lost my headphones."),
    ("genre","ˈʒɒnrə","żonrə","gatunek","Jazz is my favourite genre."),
    ("singer","ˈsɪŋə","syngə","piosenkarz","She's a great singer."),
    ("hum","hʌm","ham","nucić","I keep humming that tune."),
],
"travel-planning": [
    ("destination","ˌdestɪˈneɪʃn","destynejszn","miejsce docelowe","Choose your destination."),
    ("itinerary","aɪˈtɪnərəri","ajtynerery","plan podróży","Send me the itinerary."),
    ("book","bʊk","buk","zarezerwować","Book your flight early."),
    ("flight","flaɪt","flajt","lot","The flight is at 6 am."),
    ("insurance","ɪnˈʃʊərəns","inszuərens","ubezpieczenie","Get travel insurance."),
    ("passport","ˈpɑːspɔːt","paaspoot","paszport","Check your passport."),
    ("visa","ˈviːzə","wijzə","wiza","Do I need a visa?"),
    ("currency","ˈkʌrənsi","karensy","waluta","Exchange currency at home."),
    ("packing","ˈpækɪŋ","pekyng","pakowanie","I hate packing."),
    ("souvenir","ˌsuːvəˈnɪə","suuwenia","pamiątka","Buy a small souvenir."),
],
"sightseeing": [
    ("landmark","ˈlændmɑːk","lendmaak","punkt orientacyjny","A famous landmark."),
    ("guide","ɡaɪd","gajd","przewodnik","Our guide was funny."),
    ("museum","mjuˈziːəm","mjuzyem","muzeum","The museum is free on Sunday."),
    ("monument","ˈmɒnjumənt","monjument","pomnik","An old monument."),
    ("tour","tʊə","tuə","wycieczka","Book a walking tour."),
    ("attraction","əˈtrækʃn","atrekszn","atrakcja","Top attractions in the city."),
    ("crowded","ˈkraʊdɪd","krałdyd","zatłoczony","It was very crowded."),
    ("admission","ədˈmɪʃn","admyszn","wstęp","Admission is 20 zł."),
    ("souvenir","ˌsuːvəˈnɪə","suuwenia","pamiątka","A nice souvenir shop."),
    ("photograph","ˈfəʊtəɡrɑːf","foutograaf","fotografia","Take a photograph here."),
],
"driving-cars": [
    ("traffic","ˈtræfɪk","trefyk","ruch uliczny","Heavy traffic this morning."),
    ("jam","dʒæm","dżem","korek","We're stuck in a jam."),
    ("petrol","ˈpetrəl","petrol","benzyna","Fill up with petrol."),
    ("highway","ˈhaɪweɪ","hajłej","autostrada","Take the highway."),
    ("speed limit","spiːd ˈlɪmɪt","spijd lymyt","limit prędkości","Watch the speed limit."),
    ("seatbelt","ˈsiːtbelt","sijtbelt","pas bezpieczeństwa","Fasten your seatbelt."),
    ("park","pɑːk","paak","parkować","I can't park here."),
    ("license","ˈlaɪsns","lajsns","prawo jazdy","Show your license."),
    ("breakdown","ˈbreɪkdaʊn","brejkdałn","awaria","Car breakdown again."),
    ("overtake","ˌəʊvəˈteɪk","ouwətejk","wyprzedzać","Don't overtake here."),
],
"education": [
    ("course","kɔːs","koos","kurs","I signed up for a course."),
    ("degree","dɪˈɡriː","dygrij","stopień / dyplom","She has a master's degree."),
    ("exam","ɪɡˈzæm","igzem","egzamin","I have an exam next week."),
    ("assignment","əˈsaɪnmənt","asajnment","zadanie / praca zaliczeniowa","Hand in the assignment."),
    ("lecture","ˈlektʃə","lekczə","wykład","Boring lecture today."),
    ("tutor","ˈtjuːtə","tjuutə","korepetytor","I hired a tutor."),
    ("scholarship","ˈskɒləʃɪp","skoloszyp","stypendium","She got a scholarship."),
    ("graduate","ˈɡrædʒuət","gredżuət","absolwent / kończyć studia","I graduate in June."),
    ("major","ˈmeɪdʒə","mejdżə","kierunek studiów","I majored in economics."),
    ("research","rɪˈsɜːtʃ","risyrcz","badania","I'm doing research on bees."),
],
"online-learning": [
    ("platform","ˈplætfɔːm","pletfoom","platforma","A great learning platform."),
    ("subscription","səbˈskrɪpʃn","sabskrypszn","subskrypcja","Monthly subscription."),
    ("module","ˈmɒdjuːl","modjul","moduł","Finish the module."),
    ("quiz","kwɪz","kłyz","quiz","Take the quiz."),
    ("certificate","səˈtɪfɪkət","sytyfykət","certyfikat","Get a certificate at the end."),
    ("self-paced","self peɪst","self pejst","własne tempo","The course is self-paced."),
    ("webinar","ˈwebɪnɑː","webynaa","webinar","Join the webinar live."),
    ("recording","rɪˈkɔːdɪŋ","rikoordyng","nagranie","Watch the recording later."),
    ("instructor","ɪnˈstrʌktə","instraktə","instruktor","The instructor is clear."),
    ("forum","ˈfɔːrəm","foorem","forum","Ask in the forum."),
],
"salary-benefits": [
    ("salary","ˈsæləri","saləri","pensja","Monthly salary."),
    ("bonus","ˈbəʊnəs","bounes","premia","Annual bonus."),
    ("raise","reɪz","rejz","podwyżka","I asked for a raise."),
    ("perks","pɜːks","pyrks","benefity","Great perks at this job."),
    ("pension","ˈpenʃn","penszn","emerytura","Pension plan included."),
    ("medical","ˈmedɪkl","medykl","medyczny","Medical insurance covered."),
    ("leave","liːv","liiw","urlop","Annual leave is 26 days."),
    ("net","net","net","netto","Net salary after tax."),
    ("gross","ɡrəʊs","grous","brutto","Gross income."),
    ("contract","ˈkɒntrækt","kontrakt","umowa","Permanent contract."),
],
"working-abroad": [
    ("relocate","ˌriːləʊˈkeɪt","ryloukejt","przeprowadzać się (do pracy)","I relocated to Berlin."),
    ("expat","ˈekspæt","ekspet","ekspat","An expat community."),
    ("work permit","wɜːk ˈpɜːmɪt","łyrk pyrmyt","zezwolenie na pracę","Apply for a work permit."),
    ("residence","ˈrezɪdəns","rezydens","miejsce zamieszkania","Residence permit."),
    ("culture shock","ˈkʌltʃə ʃɒk","kalczə szok","szok kulturowy","I had a culture shock."),
    ("integration","ˌɪntɪˈɡreɪʃn","intygrejszn","integracja","Integration takes time."),
    ("homesick","ˈhəʊmsɪk","houmsyk","tęskniący za domem","I felt homesick."),
    ("commute","kəˈmjuːt","komjut","dojazd","Long commute here."),
    ("rent","rent","rent","wynajem","Rent abroad is high."),
    ("local","ˈləʊkl","loukl","lokalny","Try the local food."),
],
"customer-service": [
    ("support","səˈpɔːt","sapoort","wsparcie","Contact support."),
    ("ticket","ˈtɪkɪt","tykyt","zgłoszenie","Open a support ticket."),
    ("issue","ˈɪʃuː","iszju","problem","Describe the issue."),
    ("agent","ˈeɪdʒənt","ejdżent","agent / pracownik","Talk to an agent."),
    ("escalate","ˈeskəleɪt","eskelejt","eskalować","Escalate to a manager."),
    ("resolve","rɪˈzɒlv","rizolw","rozwiązać","Resolve the issue today."),
    ("query","ˈkwɪəri","kłiry","zapytanie","Send your query by email."),
    ("response","rɪˈspɒns","rispons","odpowiedź","Quick response time."),
    ("hotline","ˈhɒtlaɪn","hotlajn","infolinia","Call the hotline."),
    ("satisfaction","ˌsætɪsˈfækʃn","satysfekszn","satysfakcja","Customer satisfaction survey."),
],
"complaints": [
    ("complaint","kəmˈpleɪnt","kompleejnt","reklamacja","File a complaint."),
    ("faulty","ˈfɔːlti","foolty","wadliwy","The product is faulty."),
    ("refund","ˈriːfʌnd","ryfand","zwrot pieniędzy","I demand a refund."),
    ("replacement","rɪˈpleɪsmənt","riplejsment","wymiana","Send a replacement."),
    ("damaged","ˈdæmɪdʒd","damydżd","uszkodzony","The item arrived damaged."),
    ("unacceptable","ˌʌnəkˈseptəbl","anakseptebl","nie do zaakceptowania","This is unacceptable."),
    ("disappointed","ˌdɪsəˈpɔɪntɪd","disapojntyd","rozczarowany","I'm very disappointed."),
    ("manager","ˈmænɪdʒə","menydżə","kierownik","Let me speak to the manager."),
    ("warranty","ˈwɒrənti","łoronty","gwarancja","Still under warranty."),
    ("claim","kleɪm","klejm","roszczenie","File a claim."),
],
"apologizing": [
    ("sorry","ˈsɒri","sory","przepraszam","I'm really sorry."),
    ("apologise","əˈpɒlədʒaɪz","apolodżajz","przepraszać","I apologise for the delay."),
    ("mistake","mɪˈsteɪk","mystejk","błąd","My mistake."),
    ("forgive","fəˈɡɪv","fəgyw","wybaczać","Please forgive me."),
    ("regret","rɪˈɡret","rygret","żałować","I regret saying that."),
    ("explain","ɪkˈspleɪn","ekspleejn","wyjaśniać","Let me explain."),
    ("misunderstand","ˌmɪsʌndəˈstænd","mysandəstend","źle zrozumieć","I misunderstood you."),
    ("intention","ɪnˈtenʃn","intenszn","intencja","That wasn't my intention."),
    ("make up for","meɪk ʌp fɔː","mejk ap foo","wynagrodzić","Let me make up for it."),
    ("excuse","ɪkˈskjuːz","ekskjuz","wymówka / usprawiedliwiać","No excuses."),
],
"appointments": [
    ("schedule","ˈʃedjuːl","szedjul","umawiać / harmonogram","Let's schedule a call."),
    ("reschedule","ˌriːˈʃedjuːl","riszedjul","przekładać termin","Can we reschedule?"),
    ("cancel","ˈkænsl","kensl","odwołać","I need to cancel."),
    ("confirm","kənˈfɜːm","konfyrm","potwierdzić","Please confirm by email."),
    ("availability","əˌveɪləˈbɪləti","awejlebylyty","dostępność","What's your availability?"),
    ("slot","slɒt","slot","termin / okienko","Any slots tomorrow?"),
    ("calendar","ˈkælɪndə","kalyndə","kalendarz","Check my calendar."),
    ("invite","ɪnˈvaɪt","inwajt","zapraszać","I sent you an invite."),
    ("remind","rɪˈmaɪnd","rimajnd","przypominać","Remind me tomorrow."),
    ("on time","ɒn taɪm","on tajm","na czas","Always be on time."),
],
"neighbours": [
    ("neighbour","ˈneɪbə","nejbə","sąsiad","My neighbour is kind."),
    ("noise","nɔɪz","nojz","hałas","Too much noise."),
    ("quiet","ˈkwaɪət","kłajet","cichy","A quiet area."),
    ("hallway","ˈhɔːlweɪ","hoolłej","korytarz","I met him in the hallway."),
    ("borrow","ˈbɒrəʊ","boroł","pożyczać","Can I borrow some sugar?"),
    ("walk","wɔːk","łook","spacer","Take a walk together."),
    ("pet","pet","pet","zwierzak","Our pet is friendly."),
    ("trash","træʃ","tresz","śmieci","Take out the trash."),
    ("parking","ˈpɑːkɪŋ","paakyng","parkowanie","Parking is a problem."),
    ("greet","ɡriːt","grijt","witać się","Always greet your neighbours."),
],
"pets": [
    ("pet","pet","pet","zwierzak","I have two pets."),
    ("dog","dɒɡ","dog","pies","My dog is a labrador."),
    ("cat","kæt","ket","kot","Our cat is grumpy."),
    ("vet","vet","wet","weterynarz","Take it to the vet."),
    ("feed","fiːd","fijd","karmić","Feed the cat at 7."),
    ("walk","wɔːk","łook","wyprowadzać","I walk my dog twice a day."),
    ("groom","ɡruːm","gruum","pielęgnować","The dog needs grooming."),
    ("puppy","ˈpʌpi","papy","szczeniak","She got a puppy."),
    ("adopt","əˈdɒpt","adopt","adoptować","We adopted a rescue dog."),
    ("breed","briːd","brijd","rasa","What breed is it?"),
],
"environment": [
    ("recycle","riːˈsaɪkl","risajkl","przetwarzać","Recycle your plastic."),
    ("pollution","pəˈluːʃn","poluszn","zanieczyszczenie","Air pollution is rising."),
    ("climate","ˈklaɪmət","klajmet","klimat","Climate change is real."),
    ("emissions","ɪˈmɪʃnz","imysznz","emisje","Reduce emissions."),
    ("renewable","rɪˈnjuːəbl","ryniueble","odnawialny","Renewable energy."),
    ("waste","weɪst","łejst","odpady","Reduce food waste."),
    ("sustainable","səˈsteɪnəbl","sastejnebl","zrównoważony","Sustainable lifestyle."),
    ("carbon","ˈkɑːbən","kaaben","węgiel (CO2)","Carbon footprint."),
    ("habitat","ˈhæbɪtæt","hebytet","środowisko (zwierząt)","Protect their habitat."),
    ("eco-friendly","ˈiːkəʊ ˈfrendli","ikou frendly","ekologiczny","An eco-friendly product."),
],
"news": [
    ("headline","ˈhedlaɪn","hedlajn","nagłówek","Today's headline."),
    ("source","sɔːs","soos","źródło","Check the source."),
    ("breaking","ˈbreɪkɪŋ","brejkyng","najnowsze (wiadomości)","Breaking news!"),
    ("update","ˈʌpdeɪt","apdejt","aktualizacja","Stay tuned for updates."),
    ("coverage","ˈkʌvərɪdʒ","kawerydż","relacja","Live coverage."),
    ("article","ˈɑːtɪkl","aatykl","artykuł","I read the full article."),
    ("scandal","ˈskændl","skendl","skandal","A political scandal."),
    ("election","ɪˈlekʃn","ilekszn","wybory","The election is next month."),
    ("press","pres","pres","prasa","The press is here."),
    ("biased","ˈbaɪəst","bajest","stronniczy","The article is biased."),
],
"personal-finance": [
    ("budget","ˈbʌdʒɪt","badżyt","budżet","Stick to your budget."),
    ("savings","ˈseɪvɪŋz","sejwyngz","oszczędności","Build your savings."),
    ("expense","ɪkˈspens","ekspens","wydatek","Cut your expenses."),
    ("invest","ɪnˈvest","inwest","inwestować","Invest in index funds."),
    ("debt","det","det","dług","Pay off your debt."),
    ("income","ˈɪnkʌm","inkam","dochód","Monthly income."),
    ("tax","tæks","teks","podatek","Pay your taxes."),
    ("interest","ˈɪntrəst","intrest","odsetki","Interest on the loan."),
    ("emergency fund","ɪˈmɜːdʒənsi fʌnd","imyrdżensi fand","fundusz awaryjny","Build an emergency fund."),
    ("retirement","rɪˈtaɪəmənt","ritajement","emerytura","Save for retirement."),
],
"insurance": [
    ("policy","ˈpɒləsi","polesy","polisa","My policy is annual."),
    ("premium","ˈpriːmiəm","prijmiem","składka","Monthly premium."),
    ("claim","kleɪm","klejm","roszczenie / zgłosić","File a claim."),
    ("coverage","ˈkʌvərɪdʒ","kawerydż","zakres ochrony","Full coverage."),
    ("deductible","dɪˈdʌktəbl","didaktebl","udział własny","High deductible."),
    ("liability","ˌlaɪəˈbɪləti","lajebylyty","odpowiedzialność","Liability insurance."),
    ("renewal","rɪˈnjuːəl","ryniuel","odnowienie","Policy renewal."),
    ("broker","ˈbrəʊkə","broukə","broker","Talk to your broker."),
    ("damage","ˈdæmɪdʒ","damydż","szkoda","Report the damage."),
    ("compensation","ˌkɒmpenˈseɪʃn","kompensejszn","odszkodowanie","Receive compensation."),
],
"life-goals": [
    ("goal","ɡəʊl","goul","cel","Set a clear goal."),
    ("plan","plæn","plen","plan","Make a long-term plan."),
    ("achieve","əˈtʃiːv","aczijw","osiągać","Achieve your dreams."),
    ("dream","driːm","drijm","marzenie","Follow your dream."),
    ("priority","praɪˈɒrəti","prajorety","priorytet","Family is a priority."),
    ("retirement","rɪˈtaɪəmənt","ritajement","emerytura","Plan for retirement."),
    ("legacy","ˈleɡəsi","legesy","spuścizna","Build a legacy."),
    ("regret","rɪˈɡret","rygret","żałować","No regrets."),
    ("purpose","ˈpɜːpəs","pyrpes","cel (sens)","Find your purpose."),
    ("milestone","ˈmaɪlstəʊn","majlstoun","kamień milowy","A life milestone."),
],
}

# Per-topic dialog (1 main, ~6 lines). Second dialog is built from same template with slight var.
DIALOGS = {
"small-talk": [
    ("A","Lovely weather today, isn't it?","Ładna pogoda dziś, prawda?"),
    ("B","Yes, it's such a nice change after all that rain.","Tak, taka miła odmiana po tym deszczu."),
    ("A","Are you doing anything special this weekend?","Planujesz coś szczególnego na weekend?"),
    ("B","Just relaxing at home. How about you?","Po prostu odpoczynek w domu. A ty?"),
    ("A","I might go for a walk in the park if it stays sunny.","Może wybiorę się na spacer, jeśli słońce zostanie."),
    ("B","Sounds great. Enjoy your weekend!","Brzmi świetnie. Miłego weekendu!"),
],
"job-interview": [
    ("Interviewer","Thanks for coming in. Could you tell me about your background?","Dziękuję, że pan przyszedł. Czy może pan opowiedzieć o swoim doświadczeniu?"),
    ("Candidate","Sure. I've been working as a project manager for five years.","Oczywiście. Pracuję jako kierownik projektu od pięciu lat."),
    ("Interviewer","What would you say is your biggest strength?","Co pan uważa za swoją największą mocną stronę?"),
    ("Candidate","I'd say it's keeping the team motivated under pressure.","Powiedziałbym, że to utrzymywanie motywacji zespołu pod presją."),
    ("Interviewer","And a weakness you're working on?","A nad jaką słabością pan pracuje?"),
    ("Candidate","Sometimes I take on too much. I'm learning to delegate.","Czasem biorę na siebie za dużo. Uczę się delegować."),
    ("Interviewer","Great. What are your salary expectations?","Świetnie. Jakie są pana oczekiwania finansowe?"),
    ("Candidate","Based on my experience, around 12,000 net.","Biorąc pod uwagę moje doświadczenie, około 12 000 netto."),
],
"office-emails": [
    ("Anna","Hi Tom, did you get the attachment I sent yesterday?","Cześć Tom, dostałeś załącznik, który wczoraj wysłałam?"),
    ("Tom","Yes, I'm going through it now. The numbers look fine.","Tak, właśnie przeglądam. Liczby wyglądają dobrze."),
    ("Anna","Great. Could you CC Mark on your reply?","Świetnie. Możesz dodać Marka do wiadomości w odpowiedzi?"),
    ("Tom","Of course. I'll send a draft for your review first.","Jasne. Najpierw wyślę szkic do twojej akceptacji."),
    ("Anna","Perfect. Don't forget the Friday deadline.","Idealnie. Nie zapomnij o piątkowym terminie."),
    ("Tom","I'm on it. Best regards.","Pracuję nad tym. Pozdrawiam."),
],
"meetings": [
    ("Host","Good morning everyone, can you all hear me?","Dzień dobry wszystkim, wszyscy mnie słyszą?"),
    ("Tom","Yes, loud and clear.","Tak, głośno i wyraźnie."),
    ("Host","Let's go through the agenda. First item: project status.","Przejdźmy do porządku obrad. Pierwszy punkt: status projektu."),
    ("Anna","We're on track but slightly over budget.","Idziemy zgodnie z planem, ale lekko przekraczamy budżet."),
    ("Host","Could you share your screen and show the numbers?","Możesz udostępnić ekran i pokazać liczby?"),
    ("Anna","Sure, one moment. Can everyone see this?","Jasne, chwilkę. Wszyscy to widzą?"),
    ("Host","Great. Let's move to the next agenda item.","Świetnie. Przejdźmy do następnego punktu."),
],
"doctors-visit": [
    ("Doctor","Good morning. What seems to be the problem?","Dzień dobry. Co panu dolega?"),
    ("Patient","I've had a sore throat and a cough for three days.","Boli mnie gardło i kaszlę od trzech dni."),
    ("Doctor","Any fever or headache?","Czy ma pan gorączkę albo ból głowy?"),
    ("Patient","A bit of a headache and I feel dizzy sometimes.","Lekki ból głowy i czasem mam zawroty głowy."),
    ("Doctor","Let me check your blood pressure. It's normal.","Sprawdzę ciśnienie. Jest w normie."),
    ("Doctor","I'll give you a prescription. Take it three times a day.","Wypiszę receptę. Trzy razy dziennie."),
    ("Patient","Thank you, doctor. I hope I'll get better soon.","Dziękuję panie doktorze. Mam nadzieję, że szybko wyzdrowieję."),
],
"at-the-airport": [
    ("Agent","Good morning, your passport and boarding pass please.","Dzień dobry, paszport i karta pokładowa proszę."),
    ("Traveller","Here you are. Is the flight on time?","Proszę bardzo. Lot jest punktualnie?"),
    ("Agent","I'm afraid it's delayed by one hour due to weather.","Niestety opóźniony o godzinę z powodu pogody."),
    ("Traveller","Oh no. Will I miss my layover in Munich?","O nie. Czy zdążę na przesiadkę w Monachium?"),
    ("Agent","You should be fine — your layover is three hours.","Powinno być dobrze — ma pan trzy godziny przesiadki."),
    ("Traveller","Great. Which gate should I go to?","Świetnie. Do której bramki mam iść?"),
    ("Agent","Gate B12. Security is to your left.","Bramka B12. Kontrola po lewej."),
],
"hotel": [
    ("Guest","Hi, I have a booking under Nowak.","Cześć, mam rezerwację na nazwisko Nowak."),
    ("Receptionist","Welcome. A double room for two nights, correct?","Witam. Pokój dwuosobowy na dwie noce, zgadza się?"),
    ("Guest","That's right. What's the Wi-Fi password?","Tak. Jakie jest hasło do Wi-Fi?"),
    ("Receptionist","It's on this card. Breakfast is complimentary.","Jest na tej karteczce. Śniadanie gratis."),
    ("Guest","Great. What time is check-out?","Świetnie. O której wymeldowanie?"),
    ("Receptionist","Check-out is by 11. Enjoy your stay!","Wymeldowanie do 11. Miłego pobytu!"),
],
"renting-flat": [
    ("Tenant","Hello, I'm interested in the flat you're listing.","Dzień dobry, interesuje mnie wystawione mieszkanie."),
    ("Landlord","Sure, when would you like to book a viewing?","Jasne, kiedy chciałby pan umówić oglądanie?"),
    ("Tenant","Tomorrow at 6, if that works. Is it fully furnished?","Jutro o 18, jeśli pasuje. Czy jest umeblowane?"),
    ("Landlord","Yes, fully furnished. Rent is 3,000 plus utilities.","Tak, w pełni umeblowane. Czynsz 3000 plus media."),
    ("Tenant","And the deposit?","A kaucja?"),
    ("Landlord","Two months' rent. Standard one-year lease.","Dwa czynsze. Standardowa umowa roczna."),
    ("Tenant","Sounds reasonable. See you tomorrow.","Brzmi rozsądnie. Do jutra."),
],
"banking": [
    ("Clerk","Good morning, how can I help you?","Dzień dobry, w czym mogę pomóc?"),
    ("Customer","I'd like to make a transfer to a foreign account.","Chciałbym zrobić przelew na konto zagraniczne."),
    ("Clerk","Of course. Please fill in this form.","Oczywiście. Proszę wypełnić ten formularz."),
    ("Customer","Could you also check my balance?","Czy może pan też sprawdzić moje saldo?"),
    ("Clerk","Your balance is 4,250 zł. Anything else?","Saldo to 4 250 zł. Coś jeszcze?"),
    ("Customer","Yes, I lost my card. Can I block it?","Tak, zgubiłem kartę. Mogę ją zablokować?"),
    ("Clerk","I'll block it now and order a new one.","Zablokuję ją od razu i zamówię nową."),
],
"shopping": [
    ("Customer","Hi, I'd like to return these shoes. They're too tight.","Dzień dobry, chciałbym zwrócić te buty. Są za ciasne."),
    ("Cashier","Do you have the receipt?","Czy ma pan paragon?"),
    ("Customer","Yes, here it is. Can I get a refund?","Tak, proszę. Mogę dostać zwrot pieniędzy?"),
    ("Cashier","Sure, or you can exchange them for a bigger size.","Jasne, albo może je pan wymienić na większy rozmiar."),
    ("Customer","Do you have these in 43?","Czy ma pan te w 43?"),
    ("Cashier","Let me check… yes, and they're on sale today.","Sprawdzę… tak, i są dziś na wyprzedaży."),
    ("Customer","Great, I'll take them.","Świetnie, biorę."),
],
"restaurant": [
    ("Waiter","Good evening. Do you have a reservation?","Dobry wieczór. Czy ma pan rezerwację?"),
    ("Guest","Yes, a table for two under Kowalski.","Tak, stolik dla dwóch na Kowalski."),
    ("Waiter","Right this way. Here's the menu.","Tędy proszę. Oto menu."),
    ("Guest","Do you have any vegetarian starters?","Czy są jakieś wegetariańskie przystawki?"),
    ("Waiter","Yes, the bruschetta and the tomato soup.","Tak, bruschetta i zupa pomidorowa."),
    ("Guest","Great. We'll have both, and the pasta as a main course.","Świetnie. Bierzemy obie i makaron jako danie główne."),
    ("Waiter","Excellent choice. Any allergies?","Doskonały wybór. Jakieś alergie?"),
],
"negotiations": [
    ("A","Thanks for the offer, but it's a bit low.","Dzięki za ofertę, ale jest trochę za niska."),
    ("B","What did you have in mind?","Co pan miał na myśli?"),
    ("A","Around 15% higher, plus a longer contract.","Około 15% więcej, plus dłuższy kontrakt."),
    ("B","That's tough. Can we compromise at 10%?","To trudne. Czy możemy się dogadać na 10%?"),
    ("A","If you cover the training costs, we have a deal.","Jeśli pokryjecie koszty szkolenia, mamy umowę."),
    ("B","Done. Let's sign next week.","Zgoda. Podpisujemy w przyszłym tygodniu."),
],
"project-management": [
    ("PM","Where are we on the milestone?","Gdzie jesteśmy z kamieniem milowym?"),
    ("Dev","Almost done. We have two tasks left in the sprint.","Prawie gotowe. Zostały dwa zadania w sprincie."),
    ("PM","Any risks I should know about?","Jakieś ryzyka, o których powinienem wiedzieć?"),
    ("Dev","The new requirement could cause scope creep.","Nowy wymóg może powodować rozrastanie zakresu."),
    ("PM","Let's update the stakeholders today.","Zaktualizujmy dziś interesariuszy."),
    ("Dev","Will do. Kick-off for phase two is next Monday.","Zrobimy. Start drugiego etapu w poniedziałek."),
],
"remote-work": [
    ("A","How's your home office set-up?","Jak twoje biuro domowe?"),
    ("B","Pretty good. No commute, but I miss the team.","Całkiem dobrze. Brak dojazdu, ale brakuje mi zespołu."),
    ("A","Do you still have a daily standup?","Czy macie codzienne standupy?"),
    ("B","Yes, at 9:30 on Slack.","Tak, o 9:30 na Slacku."),
    ("A","Watch out for burnout — take breaks.","Uważaj na wypalenie — rób przerwy."),
    ("B","Thanks. We're going hybrid next month anyway.","Dzięki. I tak przechodzimy na hybrydę w przyszłym miesiącu."),
],
"public-transport": [
    ("A","Excuse me, which platform for the 5:15 train?","Przepraszam, z którego peronu odjeżdża pociąg 5:15?"),
    ("B","Platform 4. But there's a 10-minute delay.","Peron 4. Ale jest 10 minut opóźnienia."),
    ("A","Do I need to transfer?","Czy muszę się przesiąść?"),
    ("B","Yes, change at Central Station.","Tak, przesiadka na dworcu głównym."),
    ("A","How much is a single ticket?","Ile kosztuje bilet jednorazowy?"),
    ("B","Four zlotys. The machine is over there.","Cztery złote. Automat jest tam."),
],
"family-life": [
    ("A","How are your kids doing?","Jak twoje dzieci?"),
    ("B","Busy. The teenager argues, the toddler doesn't sleep.","Zajęte. Nastolatek się kłóci, maluch nie śpi."),
    ("A","Do you get any help from relatives?","Pomagają wam jacyś krewni?"),
    ("B","Yes, my in-laws are amazing.","Tak, teściowie są wspaniali."),
    ("A","That's lovely. We share the housework with my partner.","To miłe. My z partnerem dzielimy się pracami domowymi."),
    ("B","Same here. Close families make it work.","U nas tak samo. Bliskie rodziny dają radę."),
],
"hobbies": [
    ("A","What do you do in your free time?","Co robisz w wolnym czasie?"),
    ("B","I'm into photography and hiking.","Lubię fotografię i wędrówki."),
    ("A","Sounds great. I'm an amateur baker.","Brzmi świetnie. Ja amatorsko piekę."),
    ("B","Oh, you should try sourdough.","Powinieneś spróbować chleba na zakwasie."),
    ("A","Maybe. I find gardening more relaxing.","Może. Bardziej relaksuje mnie ogrodnictwo."),
    ("B","Each to their own passion.","Każdy ma swoją pasję."),
],
"health-gym": [
    ("Trainer","How was your workout today?","Jak twój dziś trening?"),
    ("Client","Hard. My muscles are sore.","Ciężko. Mięśnie mnie bolą."),
    ("Trainer","Did you stretch after?","Rozciągałeś się po treningu?"),
    ("Client","A little. I prefer cardio over weights.","Trochę. Wolę cardio od ciężarów."),
    ("Trainer","Mix both. Take a rest day tomorrow.","Łącz oba. Jutro dzień przerwy."),
    ("Client","Okay. I'll watch my calories too.","Dobra. Popilnuję też kalorii."),
],
"weather": [
    ("A","Have you seen the forecast?","Widziałeś prognozę?"),
    ("B","Yes, a heatwave is coming next week.","Tak, w przyszłym tygodniu fala upałów."),
    ("A","I prefer a light breeze and clear sky.","Wolę lekki wiaterek i czyste niebo."),
    ("B","Me too. But last night's thunderstorm was scary.","Ja też. Ale wczorajsza burza była straszna."),
    ("A","At least no blizzard this winter.","Przynajmniej tej zimy nie było zamieci."),
    ("B","Today is just freezing — bring a jacket.","Dziś jest po prostu lodowato — weź kurtkę."),
],
"tech-gadgets": [
    ("A","My phone keeps crashing after the update.","Mój telefon się zawiesza po aktualizacji."),
    ("B","Did you make a backup before updating?","Zrobiłeś backup przed aktualizacją?"),
    ("A","Yes, in the cloud. Battery dies fast too.","Tak, w chmurze. Bateria też szybko siada."),
    ("B","Check the settings — maybe a wireless option is on.","Sprawdź ustawienia — może coś bezprzewodowego jest włączone."),
    ("A","I'll try. Where's my charger?","Spróbuję. Gdzie moja ładowarka?"),
    ("B","On the desk. Time for a new device, maybe?","Na biurku. Może czas na nowe urządzenie?"),
],
"social-media": [
    ("A","Did you see her latest post?","Widziałeś jej ostatni wpis?"),
    ("B","Yes, lots of likes and comments.","Tak, dużo polubień i komentarzy."),
    ("A","She's becoming a real influencer.","Staje się prawdziwą influencerką."),
    ("B","I just scroll for hours and forget to share.","Ja tylko przewijam godzinami i zapominam udostępniać."),
    ("A","Turn off notifications — you'll feel better.","Wyłącz powiadomienia — poczujesz się lepiej."),
    ("B","Good idea. I'll update my profile too.","Dobry pomysł. Zaktualizuję też profil."),
],
"asking-for-help": [
    ("A","Can I ask you a favour? It's a bit urgent.","Mogę cię prosić o przysługę? To dość pilne."),
    ("B","Sure, what's up?","Pewnie, o co chodzi?"),
    ("A","Could you assist me with this report?","Czy możesz mi pomóc z tym raportem?"),
    ("B","Of course. Let me guide you through it.","Jasne. Poprowadzę cię krok po kroku."),
    ("A","Could you clarify this part?","Czy możesz wyjaśnić tę część?"),
    ("B","Sure. Just give me a hint about what you need.","Pewnie. Daj mi tylko wskazówkę, czego potrzebujesz."),
    ("A","You're a lifesaver. That's very kind of you.","Jesteś moim wybawcą. To bardzo miłe."),
],
"giving-feedback": [
    ("Manager","Thanks for your work. I have some feedback.","Dzięki za pracę. Mam parę uwag."),
    ("Employee","Sure, I appreciate honest feedback.","Pewnie, doceniam szczere uwagi."),
    ("Manager","Your performance is great, but be more specific in reports.","Twoje wyniki są świetne, ale w raportach bądź bardziej konkretny."),
    ("Employee","Got it. Anything to praise?","Rozumiem. Coś do pochwały?"),
    ("Manager","Yes — your growth this year is huge.","Tak — twój rozwój w tym roku jest ogromny."),
    ("Employee","Thanks. I'll work on the improvements.","Dzięki. Popracuję nad poprawkami."),
],
"conflict-at-work": [
    ("A","I had a misunderstanding with Mark today.","Miałem dziś nieporozumienie z Markiem."),
    ("B","What happened?","Co się stało?"),
    ("A","We argued about who's responsible for the bug.","Pokłóciliśmy się o odpowiedzialność za błąd."),
    ("B","Calm down and talk to him again.","Uspokój się i porozmawiaj z nim jeszcze raz."),
    ("A","Maybe HR should mediate.","Może HR powinien zmediować."),
    ("B","Try to apologise first. Solve it like adults.","Najpierw spróbuj przeprosić. Rozwiążcie to po dorosłemu."),
],
"career-change": [
    ("A","I'm thinking of a career change.","Myślę o zmianie kariery."),
    ("B","Really? Into what?","Naprawdę? W jakim kierunku?"),
    ("A","I want to retrain as a developer.","Chcę się przekwalifikować na programistę."),
    ("B","That's a big transition. Find a mentor.","To duża zmiana. Znajdź mentora."),
    ("A","Good idea. I'll also build my network.","Dobry pomysł. Pobuduję też sieć kontaktów."),
    ("B","Maybe try a startup or go freelance first.","Może spróbuj startupu albo najpierw frilansa."),
],
"cooking": [
    ("A","What are you making?","Co przyrządzasz?"),
    ("B","A new recipe. Chop the onions, please.","Nowy przepis. Pokrój cebulę, proszę."),
    ("A","Sure. Should I fry them?","Jasne. Mam je usmażyć?"),
    ("B","Yes, then boil the pasta in the other pan.","Tak, potem ugotuj makaron na drugiej patelni."),
    ("A","Add some seasoning?","Dodać przyprawy?"),
    ("B","A pinch of salt. We'll bake the rest in the oven.","Szczyptę soli. Resztę upieczemy w piekarniku."),
],
"eating-out": [
    ("A","Let's get a takeaway tonight.","Wezmy dziś coś na wynos."),
    ("B","Sure, or we could try the new buffet.","Jasne, albo możemy spróbować nowego bufetu."),
    ("A","I'm a foodie — let's go and check the specials.","Jestem smakoszem — chodźmy zobaczyć dania dnia."),
    ("B","Their portions are huge.","Mają duże porcje."),
    ("A","We can split the bill afterwards.","Później podzielimy rachunek."),
    ("B","Deal. They have Italian cuisine I love.","Zgoda. Mają włoską kuchnię, którą uwielbiam."),
],
"holidays": [
    ("A","Happy anniversary! Here's a small gift.","Wszystkiego najlepszego z okazji rocznicy! Mały prezent."),
    ("B","Oh, thank you! Beautiful decoration too.","O, dziękuję! Piękna dekoracja też."),
    ("A","It's our tradition to celebrate with guests.","To nasza tradycja — świętujemy z gośćmi."),
    ("B","Lovely. Let's make a toast.","Pięknie. Wznieśmy toast."),
    ("A","To family and many more years!","Za rodzinę i wiele kolejnych lat!"),
    ("B","Cheers! And thanks for the invitation.","Zdrowie! I dzięki za zaproszenie."),
],
"sport": [
    ("A","Did you watch the match yesterday?","Oglądałeś wczoraj mecz?"),
    ("B","Yes, terrible referee. Our team lost 2-1.","Tak, fatalny sędzia. Nasza drużyna przegrała 2-1."),
    ("A","The coach has to change tactics.","Trener musi zmienić taktykę."),
    ("B","Their best player has an injury.","Ich najlepszy zawodnik ma kontuzję."),
    ("A","Tough opponent next week.","Trudny przeciwnik w następnym tygodniu."),
    ("B","Training is at 6. Be ready.","Trening o szóstej. Bądź gotowy."),
],
"reading": [
    ("A","What are you reading?","Co czytasz?"),
    ("B","A new novel by my favourite author.","Nową powieść mojego ulubionego autora."),
    ("A","What's the genre?","Jaki to gatunek?"),
    ("B","Sci-fi. The plot has so many twists.","Sci-fi. Fabuła ma mnóstwo zwrotów akcji."),
    ("A","I prefer biographies these days.","Ja ostatnio wolę biografie."),
    ("B","I listen to audiobooks while driving.","Ja słucham audiobooków w trakcie jazdy."),
],
"movies": [
    ("A","Have you seen the new season?","Widziałeś nowy sezon?"),
    ("B","Yes, I binge-watched it in one weekend.","Tak, obejrzałem go w jeden weekend."),
    ("A","No spoilers, please! I'm on episode three.","Bez spoilerów! Jestem przy trzecim odcinku."),
    ("B","Okay. The director made a great trailer.","Dobra. Reżyser zrobił świetny zwiastun."),
    ("A","I always watch with subtitles.","Zawsze oglądam z napisami."),
    ("B","Wait for the final scene — huge plot twist!","Poczekaj na ostatnią scenę — wielki zwrot akcji!"),
],
"music": [
    ("A","Have you heard the new album?","Słyszałeś nowy album?"),
    ("B","Yes! The lyrics are beautiful.","Tak! Tekst jest piękny."),
    ("A","My favourite band dropped a single too.","Mój ulubiony zespół też wypuścił singla."),
    ("B","I'll add it to my playlist.","Dodam go do playlisty."),
    ("A","Want to go to their concert?","Chcesz iść na ich koncert?"),
    ("B","Sure! Bring your headphones for the train.","Pewnie! Weź słuchawki do pociągu."),
],
"travel-planning": [
    ("A","Have you booked your flight yet?","Zarezerwowałeś już lot?"),
    ("B","Yes, and got travel insurance too.","Tak, i mam też ubezpieczenie."),
    ("A","Did you check your passport?","Sprawdziłeś paszport?"),
    ("B","Just renewed it. Do I need a visa for there?","Świeżo wymieniony. Czy potrzebuję wizy?"),
    ("A","No. Exchange currency before the airport.","Nie. Wymień walutę przed lotniskiem."),
    ("B","Will do. Packing is the worst part!","Zrobię. Pakowanie to najgorsze!"),
],
"sightseeing": [
    ("Guide","Welcome to the city's most famous landmark.","Witam przy najsłynniejszym zabytku miasta."),
    ("Tourist","How old is this monument?","Ile lat ma ten pomnik?"),
    ("Guide","Over 400 years. Our tour lasts two hours.","Ponad 400 lat. Nasza wycieczka trwa dwie godziny."),
    ("Tourist","Is the museum included in the admission?","Czy muzeum jest wliczone we wstęp?"),
    ("Guide","Yes. After that we'll visit the souvenir shop.","Tak. Potem odwiedzimy sklep z pamiątkami."),
    ("Tourist","It's quite crowded. Good for a photograph though.","Bardzo zatłoczono. Ale fajne na zdjęcie."),
],
"driving-cars": [
    ("A","Stuck in a jam again. The traffic is terrible.","Znów w korku. Ruch jest okropny."),
    ("B","Take the highway next time.","Następnym razem jedź autostradą."),
    ("A","I need to fill up with petrol soon.","Muszę wkrótce zatankować benzyny."),
    ("B","Watch the speed limit — there's a camera ahead.","Uważaj na limit prędkości — przed nami fotoradar."),
    ("A","Got it. Did you fasten your seatbelt?","Jasne. Zapiąłeś pas?"),
    ("B","Yes. Don't overtake here, please.","Tak. Nie wyprzedzaj tutaj, proszę."),
],
"education": [
    ("A","I signed up for an online course.","Zapisałem się na kurs online."),
    ("B","What's it about?","O czym jest?"),
    ("A","It's part of a master's degree.","To część studiów magisterskich."),
    ("B","Big assignment load?","Dużo zadań?"),
    ("A","Yes, plus an exam. I might hire a tutor.","Tak, plus egzamin. Może wezmę korepetytora."),
    ("B","Apply for a scholarship — it really helps.","Wystąp o stypendium — naprawdę pomaga."),
],
"online-learning": [
    ("A","Which platform are you using?","Jakiej platformy używasz?"),
    ("B","Coursera. Monthly subscription.","Coursera. Miesięczna subskrypcja."),
    ("A","Is it self-paced?","Czy we własnym tempie?"),
    ("B","Yes, plus live webinars with the instructor.","Tak, plus webinary na żywo z instruktorem."),
    ("A","Do you get a certificate at the end?","Dostaje się certyfikat na koniec?"),
    ("B","Yes, after the final quiz and project.","Tak, po końcowym quizie i projekcie."),
],
"salary-benefits": [
    ("A","Did you accept the offer?","Przyjąłeś ofertę?"),
    ("B","Yes, the bonus and perks were great.","Tak, premia i benefity świetne."),
    ("A","Permanent contract?","Stała umowa?"),
    ("B","Yes, with medical insurance included.","Tak, z ubezpieczeniem medycznym."),
    ("A","What about leave?","A urlop?"),
    ("B","26 days. Plus they paid a raise after six months.","26 dni. Plus dali podwyżkę po sześciu miesiącach."),
],
"working-abroad": [
    ("A","How's life as an expat?","Jak życie jako ekspat?"),
    ("B","Good, but I had a culture shock at first.","Dobrze, ale na początku miałem szok kulturowy."),
    ("A","Did you get a work permit easily?","Łatwo dostałeś zezwolenie na pracę?"),
    ("B","It took two months. Residence card is next.","Trwało dwa miesiące. Karta pobytu kolejna."),
    ("A","Do you feel homesick?","Tęsknisz za domem?"),
    ("B","Sometimes. The commute is long, but rent is okay.","Czasem. Dojazd długi, ale wynajem znośny."),
],
"customer-service": [
    ("Agent","Customer support, how can I help?","Wsparcie klienta, w czym pomóc?"),
    ("Customer","I opened a ticket two days ago and got no response.","Zgłosiłem sprawę dwa dni temu i bez odpowiedzi."),
    ("Agent","Could you give me your query number?","Proszę o numer zgłoszenia."),
    ("Customer","It's 12345. The issue isn't resolved.","12345. Problem nierozwiązany."),
    ("Agent","I'll escalate it to a manager.","Eskaluję do kierownika."),
    ("Customer","Thanks for the quick response.","Dzięki za szybką odpowiedź."),
],
"complaints": [
    ("Customer","I'd like to file a complaint. The item is faulty.","Chcę złożyć reklamację. Produkt jest wadliwy."),
    ("Clerk","I'm sorry. Was it damaged on arrival?","Przepraszam. Przyszedł uszkodzony?"),
    ("Customer","Yes. I want a refund or a replacement.","Tak. Chcę zwrotu lub wymiany."),
    ("Clerk","It's still under warranty, so we can replace it.","Jest jeszcze na gwarancji, więc możemy wymienić."),
    ("Customer","This delay is unacceptable. I'm very disappointed.","To opóźnienie nie do zaakceptowania. Jestem rozczarowany."),
    ("Clerk","I'll process your claim today.","Zajmę się pana roszczeniem dziś."),
],
"apologizing": [
    ("A","I'm really sorry, that was my mistake.","Bardzo przepraszam, to mój błąd."),
    ("B","It's okay. What happened?","W porządku. Co się stało?"),
    ("A","I misunderstood your email. Let me explain.","Źle zrozumiałem twojego maila. Pozwól mi wyjaśnić."),
    ("B","No excuses needed. Just be careful next time.","Bez wymówek. Tylko bądź ostrożniejszy następnym razem."),
    ("A","Let me make up for it.","Pozwól mi to wynagrodzić."),
    ("B","Don't worry. I forgive you.","Spokojnie. Wybaczam ci."),
],
"appointments": [
    ("A","Can we schedule a call this week?","Możemy umówić rozmowę w tym tygodniu?"),
    ("B","Sure. What's your availability?","Pewnie. Jaka jest twoja dostępność?"),
    ("A","Thursday at 3? I'll send a calendar invite.","Czwartek o 15? Wyślę zaproszenie."),
    ("B","Works for me. Please confirm by email.","Pasuje. Potwierdź mailem."),
    ("A","Confirmed. If anything changes, we can reschedule.","Potwierdzone. Jak coś, możemy przełożyć."),
    ("B","Great. Remind me on Wednesday.","Świetnie. Przypomnij mi w środę."),
],
"neighbours": [
    ("A","Morning! Quiet day for once.","Dzień dobry! Wreszcie cicho."),
    ("B","Yes, no noise from upstairs.","Tak, żadnego hałasu z góry."),
    ("A","Could I borrow some sugar?","Mogę pożyczyć cukru?"),
    ("B","Of course. Come in.","Jasne. Wejdź."),
    ("A","Thanks. Fancy a walk later?","Dzięki. Masz ochotę na spacer później?"),
    ("B","Sure. I'll take out the trash and join you.","Pewnie. Wyniosę śmieci i dołączę."),
],
"pets": [
    ("A","I just adopted a puppy.","Właśnie adoptowałem szczeniaka."),
    ("B","Cute! What breed?","Słodki! Jakiej rasy?"),
    ("A","A small mix. I have to feed him every four hours.","Niewielka mieszanka. Muszę go karmić co cztery godziny."),
    ("B","Take him to the vet for a check-up.","Zabierz go do weterynarza na kontrolę."),
    ("A","Sure. We'll walk him twice a day.","Jasne. Będziemy go wyprowadzać dwa razy dziennie."),
    ("B","Grooming once a month, too.","I pielęgnacja raz w miesiącu."),
],
"environment": [
    ("A","Air pollution is getting worse.","Zanieczyszczenie powietrza pogarsza się."),
    ("B","We need more renewable energy.","Potrzebujemy więcej odnawialnej energii."),
    ("A","I recycle, but it feels like a drop in the ocean.","Recyklinguję, ale to kropla w morzu."),
    ("B","Reduce your carbon footprint too.","Zmniejsz też swój ślad węglowy."),
    ("A","I'm trying — more eco-friendly products.","Staram się — więcej ekologicznych produktów."),
    ("B","Climate change won't wait.","Zmiany klimatu nie poczekają."),
],
"news": [
    ("A","Did you see the breaking news?","Widziałeś najnowsze wiadomości?"),
    ("B","No, what's the headline?","Nie, jaki nagłówek?"),
    ("A","A big political scandal before the election.","Wielki polityczny skandal przed wyborami."),
    ("B","Check the source — some articles are biased.","Sprawdź źródło — niektóre artykuły są stronnicze."),
    ("A","The press is everywhere now.","Prasa jest wszędzie."),
    ("B","Stay tuned for the live coverage.","Czekaj na relację na żywo."),
],
"personal-finance": [
    ("A","I built an emergency fund last year.","Zbudowałem fundusz awaryjny w zeszłym roku."),
    ("B","Smart. Are you paying off any debt?","Mądre. Spłacasz jakiś dług?"),
    ("A","Yes, then I'll invest more.","Tak, potem będę więcej inwestować."),
    ("B","Watch your expenses and stick to a budget.","Pilnuj wydatków i trzymaj się budżetu."),
    ("A","I should also save for retirement.","Powinienem też odkładać na emeryturę."),
    ("B","Right. And don't forget about taxes.","Właśnie. I nie zapomnij o podatkach."),
],
"insurance": [
    ("Broker","Would you like full coverage?","Chce pan pełen zakres ochrony?"),
    ("Customer","Yes, but the premium can't be too high.","Tak, ale składka nie może być zbyt wysoka."),
    ("Broker","With a higher deductible, the premium drops.","Z wyższym udziałem własnym składka spada."),
    ("Customer","Ok. What about liability?","Dobra. A odpowiedzialność cywilna?"),
    ("Broker","Included. Renewal is annual.","Wliczona. Odnowienie raz w roku."),
    ("Customer","If something happens, can I file a claim online?","Jeśli coś się stanie, mogę złożyć roszczenie online?"),
],
"life-goals": [
    ("A","Have you set any new life goals?","Postawiłeś sobie jakieś nowe cele życiowe?"),
    ("B","Yes — a plan for the next five years.","Tak — plan na pięć lat."),
    ("A","What's your top priority?","Co jest priorytetem?"),
    ("B","Family, then retirement savings.","Rodzina, potem oszczędności na emeryturę."),
    ("A","I want to find my real purpose.","Ja chcę znaleźć swój prawdziwy cel."),
    ("B","Hit milestones along the way and don't live with regret.","Stawiaj kamienie milowe i nie żyj z żalem."),
],
}

# --- Quiz generation helpers ---
import random as _rnd

def _shuffle(seed_str, lst):
    r = _rnd.Random(hash(seed_str) & 0xFFFFFFFF)
    out = list(lst)
    r.shuffle(out)
    return out

def _grammar_q(g, ex_idx, salt):
    """Pick a real grammar MCQ from GRAMMAR_QUIZ_POOL[title]; deterministic rotation."""
    g_title = g[0]
    pool = GRAMMAR_QUIZ_POOL.get(g_title)
    if pool:
        offset = (abs(hash(salt)) // 7) % len(pool)
        item = pool[(offset + ex_idx) % len(pool)]
        # shuffle options deterministically per (title, salt, ex_idx) to avoid pre/post overlap
        correct_text = item["options"][item["correct"]]
        opts = _shuffle(g_title + salt + str(ex_idx), list(item["options"]))
        return {
            "type": "grammar",
            "q": f"Gramatyka ({g_title}). {item['q']}",
            "options": opts,
            "correct": opts.index(correct_text),
            "explain": item["explain"],
        }
    # Fallback: old fill-in (shouldn't happen if pool covers all grammars).
    g_examples = g[2]
    if ex_idx >= len(g_examples):
        ex_idx = ex_idx % len(g_examples)
    ex = g_examples[ex_idx]
    return None


def _vocab_translate_q(vocab, idx, salt):
    w = vocab[idx % len(vocab)]
    opts = [w[3]]
    for v in vocab:
        if v[3] != w[3] and v[3] not in opts and len(opts) < 4:
            opts.append(v[3])
    opts = _shuffle(w[0] + salt, opts)
    return {
        "type": "translate",
        "q": f"Co oznacza słowo „{w[0]}\"?",
        "options": opts,
        "correct": opts.index(w[3]),
        "explain": f"„{w[0]}\" = {w[3]} (np. {w[4]})"
    }

def _idiom_q(idioms, idx, salt):
    idm = idioms[idx % len(idioms)]
    opts = [idm[1]]
    for k in IDIOM_POOL:
        if k[1] != idm[1] and k[1] not in opts and len(opts) < 4:
            opts.append(k[1])
    opts = _shuffle(idm[0] + salt, opts)
    return {
        "type": "idiom",
        "q": f"Co znaczy idiom „{idm[0]}\"?",
        "options": opts,
        "correct": opts.index(idm[1]),
        "explain": f"„{idm[0]}\" = {idm[1]}"
    }

def _fill_q(vocab, idx, salt):
    w = vocab[idx % len(vocab)]
    sentence = w[4].replace(w[0], "_____", 1)
    if "_____" not in sentence:
        sentence = f"I need to _____ this. ({w[3]})"
    opts = [w[0]]
    for v in vocab:
        if v[0] != w[0] and v[0] not in opts and len(opts) < 4:
            opts.append(v[0])
    opts = _shuffle(w[0] + "f" + salt, opts)
    return {
        "type": "fill",
        "q": f"Uzupełnij: „{sentence}\"",
        "options": opts,
        "correct": opts.index(w[0]),
        "explain": f"Pełne zdanie: „{w[4]}\""
    }

def make_pretest(vocab, idioms, grammar):
    """Pre-test: 2 vocab + 1 idiom + 3 grammar = 6 pytań (więcej gramatyki)."""
    qs = []
    qs.append(_vocab_translate_q(vocab, 0, "pre"))
    qs.append(_vocab_translate_q(vocab, 2, "pre"))
    qs.append(_idiom_q(idioms, 0, "pre"))
    for i in range(3):
        g_q = _grammar_q(grammar, i, "pre")
        if g_q: qs.append(g_q)
    return qs[:6]

def make_quiz(vocab, idioms, grammar, secondary):
    """Post-quiz: 3 vocab + 2 idiom + 2 fill + 5 grammar (3 main + 2 secondary) = 12 pytań."""
    qs = []
    for i in range(3):
        qs.append(_vocab_translate_q(vocab, 6 + i, "post"))
    for i in range(min(2, max(0, len(idioms) - 1))):
        qs.append(_idiom_q(idioms, 1 + i, "post"))
    for i in range(2):
        qs.append(_fill_q(vocab, 10 + i, "post"))
    # Grammar — using real MCQ pool; ex_idx shifted so pre/post don't overlap.
    for i in range(3):
        g_q = _grammar_q(grammar, 3 + i, "post")
        if g_q: qs.append(g_q)
    for i in range(2):
        g_q = _grammar_q(secondary, i, "post2")
        if g_q: qs.append(g_q)
    return qs[:12]


# --- Build lessons ---
def slug_id(s, n):
    return f"l{n:02d}-{s}"

def topic_vocab(topic_slug, n=25):
    core = CORE.get(topic_slug, [])
    # pad with COMMON_VOCAB, deterministic shift
    idx = abs(hash(topic_slug)) % len(COMMON_VOCAB)
    extra = []
    used = {c[0] for c in core}
    i = 0
    while len(core) + len(extra) < n and i < len(COMMON_VOCAB):
        w = COMMON_VOCAB[(idx + i) % len(COMMON_VOCAB)]
        if w[0] not in used:
            extra.append(w)
            used.add(w[0])
        i += 1
    return core + extra

def topic_idioms(topic_slug, n=5):
    idx = abs(hash(topic_slug+"i")) % len(IDIOM_POOL)
    return [IDIOM_POOL[(idx+i) % len(IDIOM_POOL)] for i in range(n)]

def topic_extra_vocab(topic_slug, n=10):
    """Different slice for 'load more'."""
    idx = (abs(hash(topic_slug+"x")) + 7) % len(COMMON_VOCAB)
    return [COMMON_VOCAB[(idx+i) % len(COMMON_VOCAB)] for i in range(n)]

def make_second_dialog(topic_pl, vocab, idioms):
    """Distinct second dialog — meta-conversation about lesson vocab/idioms."""
    v = vocab
    i = idioms
    return [
        ("A", f"Let's go deeper into '{topic_pl.lower()}'. Can you use '{v[10][0]}' in a sentence?",
              f"Wejdźmy głębiej w temat. Użyjesz słowa '{v[10][0]}' w zdaniu?"),
        ("B", v[10][4], f"Po polsku: znaczy '{v[10][3]}'."),
        ("A", f"Nice. And what about '{v[11][0]}' — when would you use it?",
              f"Świetnie. A '{v[11][0]}' — kiedy to powiesz?"),
        ("B", v[11][4] + " It means " + v[11][3] + ".",
              f"Znaczy '{v[11][3]}'."),
        ("A", f"There's also the idiom '{i[1][0]}'. Do you know it?",
              f"Jest też idiom '{i[1][0]}'. Znasz go?"),
        ("B", f"Yes — {i[1][2]} It means '{i[1][1]}'.",
              f"Tak — znaczy '{i[1][1]}'."),
        ("A", f"Last one: '{v[12][0]}'. Try a sentence.",
              f"Ostatnie: '{v[12][0]}'. Spróbuj zdania."),
        ("B", v[12][4], f"Czyli: '{v[12][3]}'."),
    ]

def make_extra_dialog(topic_pl, vocab, idioms):
    v = vocab
    i = idioms
    return [
        ("A", f"One more practice round. What does '{v[15][0]}' mean to you?",
              f"Jeszcze jedna runda. Co znaczy dla ciebie '{v[15][0]}'?"),
        ("B", v[15][4], f"Po polsku: '{v[15][3]}'."),
        ("A", f"Good. Now use '{v[16][0]}' in context.",
              f"Dobrze. A teraz '{v[16][0]}' w kontekście."),
        ("B", v[16][4] + " — basically " + v[16][3] + ".",
              f"Czyli: '{v[16][3]}'."),
        ("A", f"And the idiom '{i[2][0]}'?",
              f"A idiom '{i[2][0]}'?"),
        ("B", f"{i[2][2]} It's used when something is '{i[2][1]}'.",
              f"Używamy, gdy coś jest '{i[2][1]}'."),
        ("A", "Great progress. Let's wrap up.",
              "Świetny postęp. Kończymy."),
        ("B", "Thanks — I feel more confident now.",
              "Dzięki — czuję się pewniej."),
    ]

def make_translations(second_dialog, extra_dialog):
    """6 PL→EN drills from second + extra dialogs (NEW lines, not the main lesson dialog)."""
    out = []
    for line in second_dialog:
        if len(out) >= 4: break
        if len(line[1].split()) < 3: continue
        out.append({"pl": line[2], "en": line[1]})
    for line in extra_dialog:
        if len(out) >= 6: break
        if len(line[1].split()) < 3: continue
        out.append({"pl": line[2], "en": line[1]})
    return out

def topic_extra_idioms(topic_slug, n=2):
    idx = (abs(hash(topic_slug+"xi")) + 13) % len(IDIOM_POOL)
    return [IDIOM_POOL[(idx+i) % len(IDIOM_POOL)] for i in range(n)]

# Generate TS
def ts_string(s):
    return json.dumps(s, ensure_ascii=False)

def vocab_obj(slug, i, v):
    return ("{id:" + ts_string(f"{slug}-w{i}") + ",en:" + ts_string(v[0])
            + ",ipa:" + ts_string(v[1]) + ",plPron:" + ts_string(v[2])
            + ",pl:" + ts_string(v[3]) + ",example:" + ts_string(v[4]) + "}")

def idiom_obj(slug, i, idm):
    return ("{id:" + ts_string(f"{slug}-i{i}") + ",en:" + ts_string(idm[0])
            + ",pl:" + ts_string(idm[1]) + ",example:" + ts_string(idm[2]) + "}")

def dlg_obj(lines):
    return "{lines:[" + ",".join(
        "{speaker:" + ts_string(l[0]) + ",en:" + ts_string(l[1]) + ",pl:" + ts_string(l[2]) + "}"
        for l in lines
    ) + "]}"

def grammar_obj(g):
    return ("{title:" + ts_string(g[0]) + ",rule:" + ts_string(g[1])
            + ",examples:[" + ",".join(ts_string(e) for e in g[2]) + "]}")

def quiz_obj(qs):
    items = []
    for q in qs:
        items.append("{q:" + ts_string(q["q"])
                     + ",options:[" + ",".join(ts_string(o) for o in q["options"]) + "]"
                     + ",correct:" + str(q["correct"])
                     + ",explain:" + ts_string(q["explain"]) + "}")
    return "[" + ",".join(items) + "]"

# --- Extended content helpers (fill-blanks, translations, common mistakes) ---

MISTAKES_GENERIC = [
    ("I have 25 years.", "I am 25 years old.", "Wiek wyrażamy przez 'be', nie 'have'."),
    ("I am agree with you.", "I agree with you.", "'Agree' jest czasownikiem — bez 'am/is/are'."),
    ("She make a coffee.", "She makes a coffee.", "3. os. l.poj. w Present Simple: dodaj -s."),
]

MISTAKES_BY_GRAMMAR = {
    "Present Perfect vs Past Simple": [
        ("I have seen him yesterday.", "I saw him yesterday.", "Z 'yesterday' używamy Past Simple, nie Present Perfect."),
        ("How long do you know him?", "How long have you known him?", "Stan trwający od przeszłości do teraz = Present Perfect."),
        ("I am working here since 2020.", "I have been working here since 2020.", "Z 'since/for' używamy Present Perfect (Continuous)."),
    ],
    "First & Second Conditional": [
        ("If I will have time, I'll call.", "If I have time, I'll call.", "Po 'if' w 1st Conditional nie dajemy 'will'."),
        ("If I would be rich, I would travel.", "If I were rich, I would travel.", "2nd Conditional: po 'if' Past Simple ('were' dla wszystkich)."),
        ("If she calls me, I would help.", "If she calls me, I will help.", "Nie mieszamy 1st i 2nd Conditional."),
    ],
    "Modal verbs: must / have to / should": [
        ("You must to go.", "You must go.", "Po modal verbs nie ma 'to' (oprócz 'have to', 'ought to')."),
        ("I mustn't work tomorrow.", "I don't have to work tomorrow.", "'mustn't' = zakaz; 'don't have to' = nie musisz."),
        ("He should to call her.", "He should call her.", "'should' + bezokolicznik bez 'to'."),
    ],
    "Reported Speech": [
        ("He said me that he is tired.", "He told me that he was tired.", "'say' bez dopełnienia osobowego; 'tell' + komu."),
        ("She said she will come.", "She said she would come.", "Cofamy 'will' → 'would'."),
        ("He asked where do I live.", "He asked where I lived.", "W mowie zależnej brak inwersji i 'do/does'."),
    ],
    "Passive Voice": [
        ("The letter was wrote by Tom.", "The letter was written by Tom.", "Strona bierna: be + III forma (Past Participle)."),
        ("My car is repair now.", "My car is being repaired now.", "Present Continuous Passive: is/are being + III forma."),
        ("This house built in 1920.", "This house was built in 1920.", "Brak 'be' — to nie jest poprawna strona bierna."),
    ],
    "Used to / would for past habits": [
        ("I am used to smoke.", "I used to smoke.", "'used to' = dawniej; 'be used to + -ing' = być przyzwyczajonym."),
        ("Did you used to live here?", "Did you use to live here?", "Po 'did' wraca forma podstawowa 'use to'."),
        ("We would live in Warsaw.", "We used to live in Warsaw.", "'would' nie pasuje do stanów — tylko 'used to'."),
    ],
    "Articles: a / an / the / —": [
        ("I am engineer.", "I am an engineer.", "Przed zawodem (l.poj.) potrzebny rodzajnik 'a/an'."),
        ("She plays piano.", "She plays the piano.", "Instrumenty muzyczne — z 'the'."),
        ("The life is beautiful.", "Life is beautiful.", "Pojęcia ogólne — bez rodzajnika."),
    ],
    "Gerunds and Infinitives": [
        ("I enjoy to read.", "I enjoy reading.", "Po 'enjoy' zawsze -ing."),
        ("She decided going home.", "She decided to go home.", "Po 'decide' bezokolicznik z 'to'."),
        ("I'm interested to learn French.", "I'm interested in learning French.", "Po przyimku zawsze -ing."),
    ],
    "Future forms: will / going to / Present Continuous": [
        ("I will meet Tom tomorrow at 7.", "I'm meeting Tom tomorrow at 7.", "Ustalony plan = Present Continuous."),
        ("Look at the clouds — it will rain.", "Look at the clouds — it's going to rain.", "Przewidywanie z dowodu = 'going to'."),
        ("I think I going to help.", "I think I will help.", "Decyzja teraz = 'will'."),
    ],
    "Comparatives and Superlatives": [
        ("She is more taller than me.", "She is taller than me.", "Nie łączymy 'more' z formą -er."),
        ("This is the most easy task.", "This is the easiest task.", "Krótkie przymiotniki: -est."),
        ("My English is gooder.", "My English is better.", "'good' jest nieregularne: good → better → best."),
    ],
    "Present Perfect Continuous": [
        ("I am learning English for 2 years.", "I have been learning English for 2 years.", "'for/since' = Present Perfect (Continuous)."),
        ("She has been knowing him for years.", "She has known him for years.", "Stany (know/like) nie używają formy ciągłej."),
        ("It rains all day.", "It has been raining all day.", "Czynność trwająca do teraz = PPC."),
    ],
    "Relative Clauses (who / which / that)": [
        ("The man which called you is here.", "The man who called you is here.", "Osoby = 'who/that', nie 'which'."),
        ("My brother who lives in Paris is a doctor.", "My brother, who lives in Paris, is a doctor.", "Non-defining wymaga przecinków."),
        ("The book what I bought is great.", "The book that I bought is great.", "'what' nie jest zaimkiem względnym."),
    ],
    "Question tags": [
        ("You're coming, isn't it?", "You're coming, aren't you?", "Powtarzamy operator i podmiot."),
        ("He doesn't smoke, doesn't he?", "He doesn't smoke, does he?", "Przeczenie → twierdząca tag."),
        ("She can drive, can she?", "She can drive, can't she?", "Twierdzenie → przecząca tag."),
    ],
    "So / Such / Too / Enough": [
        ("She is so kind person.", "She is such a kind person.", "Przed rzeczownikiem używamy 'such'."),
        ("This coffee is enough hot.", "This coffee is hot enough.", "'enough' stoi po przymiotniku."),
        ("It's too much cold.", "It's too cold.", "'too' bez 'much' przed przymiotnikiem."),
    ],
    "Phrasal verbs in business": [
        ("Let's put the meeting off it.", "Let's put off the meeting.", "Nie powtarzamy dopełnienia po phrasal verb."),
        ("I will look the issue.", "I will look into the issue.", "'look into' = zbadać; nie pomijaj 'into'."),
        ("She came with a great idea.", "She came up with a great idea.", "'come up with' = wymyślić — pełna fraza."),
    ],
    "Third Conditional": [
        ("If I would have studied, I would have passed.", "If I had studied, I would have passed.", "Po 'if' Past Perfect, bez 'would'."),
        ("If she had call, I would help.", "If she had called, I would have helped.", "Cała struktura w przeszłości: had + III, would have + III."),
        ("If we didn't take a taxi, we would miss the flight.", "If we hadn't taken a taxi, we would have missed the flight.", "Hipoteza o przeszłości = 3rd Conditional."),
    ],
    "Quantifiers: much / many / a few / a little": [
        ("How many sugar do you take?", "How much sugar do you take?", "Sugar jest niepoliczalne — 'much'."),
        ("I have much friends.", "I have many friends.", "Friends jest policzalne — 'many'."),
        ("We have a little time.", "We have little time.", "'a little' = trochę; 'little' = mało."),
    ],
    "Wish + Past / Past Perfect": [
        ("I wish I know the answer.", "I wish I knew the answer.", "Po 'wish' (teraz) używamy Past Simple."),
        ("I wish I would studied harder.", "I wish I had studied harder.", "Żal o przeszłość: Past Perfect."),
        ("I wish you don't interrupt me.", "I wish you wouldn't interrupt me.", "Irytujące zachowanie: 'wouldn't'."),
    ],
    "Linking words: although / however / despite": [
        ("Despite it was raining, we walked.", "Although it was raining, we walked. / Despite the rain, we walked.", "'despite' + noun/-ing, nie zdanie."),
        ("Although, it was cold.", "Although it was cold, we walked.", "'although' to spójnik — łączy dwa zdania."),
        ("It was cold, although we walked.", "It was cold; however, we walked.", "Tu pasuje 'however' (zaprzeczenie po średniku)."),
    ],
    "Indirect / Embedded questions": [
        ("Could you tell me where is the station?", "Could you tell me where the station is?", "W pytaniach pośrednich szyk twierdzący."),
        ("Do you know what time does it start?", "Do you know what time it starts?", "Brak 'do/does' w pytaniu pośrednim."),
        ("I wonder is she coming.", "I wonder if she is coming.", "Po 'wonder' używamy 'if/whether'."),
    ],
}

def mistakes_for(g_title):
    return MISTAKES_BY_GRAMMAR.get(g_title, MISTAKES_GENERIC)

def make_fill_blanks(vocab, dialog):
    """Build 6 fill-in-the-blank items from vocab examples (replace target word with ___)."""
    items = []
    used = set()
    for v in vocab:
        if len(items) >= 6: break
        en, _, _, pl, example = v[0], v[1], v[2], v[3], v[4]
        target = en
        # try whole-word replace, case-insensitive
        low = example.lower()
        idx = low.find(target.lower())
        if idx == -1: continue
        if target.lower() in used: continue
        used.add(target.lower())
        sentence = example[:idx] + "_____" + example[idx+len(target):]
        items.append({
            "sentence": sentence,
            "answer": target,
            "hint": pl,
            "full": example,
        })
    # fallback to dialog if not enough
    if len(items) < 4:
        for line in dialog:
            if len(items) >= 4: break
            words = line[1].split()
            if len(words) < 5: continue
            mid = words[len(words)//2].strip(".,!?")
            if len(mid) < 4 or mid.lower() in used: continue
            used.add(mid.lower())
            sentence = line[1].replace(mid, "_____", 1)
            items.append({"sentence": sentence, "answer": mid, "hint": line[2], "full": line[1]})
    return items


def fill_obj(f):
    return ("{sentence:" + ts_string(f["sentence"]) + ",answer:" + ts_string(f["answer"])
            + ",hint:" + ts_string(f["hint"]) + ",full:" + ts_string(f["full"]) + "}")

def trans_obj(t):
    return "{pl:" + ts_string(t["pl"]) + ",en:" + ts_string(t["en"]) + "}"

def mistake_obj(m):
    return "{wrong:" + ts_string(m[0]) + ",right:" + ts_string(m[1]) + ",note:" + ts_string(m[2]) + "}"

OUT = []
OUT.append("""// AUTO-GENERATED by scripts/gen_lessons.py — do not edit by hand.
export interface BuiltinVocab { id: string; en: string; ipa: string; plPron: string; pl: string; example: string; }
export interface BuiltinIdiom { id: string; en: string; pl: string; example: string; }
export interface BuiltinDialogLine { speaker: string; en: string; pl: string; }
export interface BuiltinDialog { lines: BuiltinDialogLine[]; }
export interface BuiltinGrammar { title: string; rule: string; examples: string[]; }
export interface BuiltinQuizQ { q: string; options: string[]; correct: number; explain: string; }
export interface BuiltinFillBlank { sentence: string; answer: string; hint: string; full: string; }
export interface BuiltinTranslation { pl: string; en: string; }
export interface BuiltinMistake { wrong: string; right: string; note: string; }
export interface BuiltinLesson {
  id: string;
  number: number;
  level: "B1" | "B2";
  topic: string;
  summary: string;
  vocab: BuiltinVocab[];
  idioms: BuiltinIdiom[];
  dialogs: BuiltinDialog[];
  grammar: BuiltinGrammar;
  secondaryGrammar: BuiltinGrammar;
  commonMistakes: BuiltinMistake[];
  fillBlanks: BuiltinFillBlank[];
  translations: BuiltinTranslation[];
  quiz: BuiltinQuizQ[];
  pretest: BuiltinQuizQ[];
  extraVocab: BuiltinVocab[];
  extraIdioms: BuiltinIdiom[];
  extraDialog: BuiltinDialog;
}
""")

OUT.append("export const BUILTIN_LESSONS: BuiltinLesson[] = [\n")

for n, (slug, title_pl, level) in enumerate(TOPICS, start=1):
    lid = slug_id(slug, n)
    vocab = topic_vocab(slug, 25)
    idioms = topic_idioms(slug, 5)
    extraV = topic_extra_vocab(slug, 10)
    extraI = topic_extra_idioms(slug, 2)
    grammar = GRAMMAR_POOL[(n-1) % len(GRAMMAR_POOL)]
    secondary = GRAMMAR_POOL[(n-1+7) % len(GRAMMAR_POOL)]
    dialog1 = DIALOGS[slug]
    dialog2 = make_second_dialog(title_pl, vocab, idioms)
    extraD = make_extra_dialog(title_pl, vocab, idioms)
    quiz = make_quiz(vocab, idioms, grammar, secondary)
    pretest = make_pretest(vocab, idioms, grammar)
    fills = make_fill_blanks(vocab, dialog1)
    trans = make_translations(dialog2, extraD)
    mistakes = mistakes_for(grammar[0])

    OUT.append("{")
    OUT.append("id:" + ts_string(lid) + ",")
    OUT.append("number:" + str(n) + ",")
    OUT.append("level:" + ts_string(level) + ",")
    OUT.append("topic:" + ts_string(f"{n:02d}. {title_pl}") + ",")
    OUT.append("summary:" + ts_string(f"Poziom {level}. Lekcja {n} z 50 — codzienne sytuacje i praca: {title_pl.lower()}.") + ",")
    OUT.append("vocab:[" + ",".join(vocab_obj(lid, i, v) for i, v in enumerate(vocab)) + "],")
    OUT.append("idioms:[" + ",".join(idiom_obj(lid, i, idm) for i, idm in enumerate(idioms)) + "],")
    OUT.append("dialogs:[" + dlg_obj(dialog1) + "," + dlg_obj(dialog2) + "],")
    OUT.append("grammar:" + grammar_obj(grammar) + ",")
    OUT.append("secondaryGrammar:" + grammar_obj(secondary) + ",")
    OUT.append("commonMistakes:[" + ",".join(mistake_obj(m) for m in mistakes) + "],")
    OUT.append("fillBlanks:[" + ",".join(fill_obj(f) for f in fills) + "],")
    OUT.append("translations:[" + ",".join(trans_obj(t) for t in trans) + "],")
    OUT.append("quiz:" + quiz_obj(quiz) + ",")
    OUT.append("pretest:" + quiz_obj(pretest) + ",")
    OUT.append("extraVocab:[" + ",".join(vocab_obj(lid+"-x", i, v) for i, v in enumerate(extraV)) + "],")
    OUT.append("extraIdioms:[" + ",".join(idiom_obj(lid+"-x", i, idm) for i, idm in enumerate(extraI)) + "],")
    OUT.append("extraDialog:" + dlg_obj(extraD) + ",")
    OUT.append("},\n")

OUT.append("];\n")

with open("src/content/lessons.ts", "w", encoding="utf-8") as f:
    f.write("".join(OUT))

print(f"Generated {len(TOPICS)} lessons -> src/content/lessons.ts")
print(f"File size: {os.path.getsize('src/content/lessons.ts')} bytes")

