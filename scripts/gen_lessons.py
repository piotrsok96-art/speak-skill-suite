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

# Grammar pool — used round-robin
GRAMMAR_POOL = [
    ("Present Perfect vs Past Simple",
     "Present Perfect (have/has + III forma) — czynność z przeszłości z wpływem na teraz lub bez konkretnego czasu. Past Simple — czynność zakończona w określonym momencie w przeszłości (yesterday, in 2010, last week).",
     ["I have lived here for five years.", "I lived in Berlin in 2018.", "Have you ever tried sushi?", "She didn't call me yesterday."]),
    ("First & Second Conditional",
     "First Conditional (realne): If + Present Simple, will + bezokolicznik. Second Conditional (hipotetyczne, mało prawdopodobne): If + Past Simple, would + bezokolicznik.",
     ["If it rains, I will stay home.", "If I were rich, I would travel more.", "If she calls, tell her I'm out.", "If I had more time, I would learn Spanish."]),
    ("Modal verbs: must / have to / should",
     "must — obowiązek wewnętrzny lub silna konieczność; have to — obowiązek zewnętrzny, zasada; should — rada, sugestia. Przeczenie: mustn't (zakaz) ≠ don't have to (nie musisz).",
     ["I must finish this today.", "I have to wear a uniform at work.", "You should see a doctor.", "You mustn't smoke here. / You don't have to come."]),
    ("Reported Speech",
     "Cofamy czas o jeden krok: Present → Past, Past → Past Perfect, will → would. Zmieniamy zaimki i okoliczniki czasu (now → then, today → that day, tomorrow → the next day).",
     ["He said, 'I'm tired.' → He said he was tired.", "She said, 'I will call.' → She said she would call.", "He said, 'I saw it.' → He said he had seen it."]),
    ("Passive Voice",
     "be + III forma czasownika. Używamy gdy ważniejsza jest czynność niż wykonawca. Przykłady czasów: is made, was built, has been done, will be sent.",
     ["The report is sent every Friday.", "This house was built in 1920.", "The package has been delivered.", "You will be informed by email."]),
    ("Used to / would for past habits",
     "used to + bezokolicznik — przeszłe nawyki lub stany, których już nie ma. would + bezokolicznik — tylko powtarzające się czynności (nie stany).",
     ["I used to smoke, but I quit.", "We used to live in Warsaw.", "Every summer we would visit our grandparents.", "I didn't use to like coffee."]),
    ("Articles: a / an / the / —",
     "a/an — coś nieznane, po raz pierwszy; the — coś znane, jedyne; brak rodzajnika — rzeczowniki niepoliczalne / pluralne ogólne.",
     ["I bought a car. The car is red.", "She plays the piano.", "Cats love milk.", "He's an engineer."]),
    ("Gerunds and Infinitives",
     "Po niektórych czasownikach: enjoy, avoid, finish + -ing. Po innych: want, decide, plan + to + bezokolicznik. Po prepositions zawsze -ing.",
     ["I enjoy reading.", "She decided to leave.", "I'm interested in learning French.", "He stopped to smoke. (przerwał, by zapalić) vs He stopped smoking. (rzucił palenie)"]),
    ("Future forms: will / going to / Present Continuous",
     "will — decyzja w momencie mówienia, przewidywanie. going to — plan / intencja, przewidywanie z dowodu. Present Continuous — ustalony plan z konkretnym czasem.",
     ["I'll help you with that.", "I'm going to start a new course.", "I'm meeting Tom at 7.", "Look at the clouds — it's going to rain."]),
    ("Comparatives and Superlatives",
     "Krótkie przymiotniki: -er / -est (taller, tallest). Długie: more / most (more interesting). Nieregularne: good→better→best, bad→worse→worst.",
     ["This task is easier than the last one.", "She is the most experienced in the team.", "My English is getting better.", "Today is worse than yesterday."]),
    ("Present Perfect Continuous",
     "have/has been + -ing. Czynność rozpoczęta w przeszłości, trwa do teraz lub niedawno się skończyła z widocznym skutkiem. Używamy z for / since / all day.",
     ["I have been learning English for two years.", "She has been working since 8 am.", "It's been raining all day.", "Why are you tired? — I've been running."]),
    ("Relative Clauses (who / which / that)",
     "who — osoby; which — rzeczy; that — osoby i rzeczy (w defining). Defining (bez przecinków) — niezbędne dla znaczenia. Non-defining (w przecinkach) — dodatkowa informacja.",
     ["The man who called you is here.", "The book which I bought is great.", "My brother, who lives in Paris, is a doctor.", "The car that broke down was old."]),
    ("Question tags",
     "Twierdzenie + przecząca tag; przeczenie + twierdząca tag. Powtarzamy operator (be/do/have/modal) i podmiot.",
     ["You're coming, aren't you?", "He doesn't smoke, does he?", "She can drive, can't she?", "They've finished, haven't they?"]),
    ("So / Such / Too / Enough",
     "so + adj/adv; such + (a/an) + adj + noun; too + adj (za bardzo, problem); adj + enough (wystarczająco).",
     ["It's so cold today.", "She is such a kind person.", "This coffee is too hot.", "Are you old enough to vote?"]),
    ("Phrasal verbs in business",
     "look into = zbadać; carry out = przeprowadzić; put off = odłożyć; bring up = poruszyć temat; go through = przejrzeć; come up with = wymyślić.",
     ["I'll look into the issue.", "We carried out a survey.", "Let's put off the meeting.", "She came up with a great idea."]),
    ("Third Conditional",
     "If + Past Perfect, would have + III forma. Hipoteza dotycząca przeszłości, której nie da się już zmienić.",
     ["If I had studied, I would have passed.", "If she had called, I would have helped.", "If we hadn't taken a taxi, we would have missed the flight."]),
    ("Quantifiers: much / many / a few / a little",
     "much + niepoliczalne (w pytaniach/przeczeniach); many + policzalne; a few + policzalne (kilka); a little + niepoliczalne (trochę); few/little (bez 'a') = mało.",
     ["How much sugar do you take?", "I have many friends.", "There are a few biscuits left.", "We have little time."]),
    ("Wish + Past / Past Perfect",
     "I wish + Past Simple — żałuję teraźniejszej sytuacji. I wish + Past Perfect — żałuję przeszłej. I wish + would — irytujące zachowanie innych.",
     ["I wish I knew the answer.", "I wish I had studied harder.", "I wish you wouldn't interrupt me.", "She wishes she had a bigger flat."]),
    ("Linking words: although / however / despite",
     "although + zdanie (Although it rained, we went out). however = jednak (samodzielne, w przecinkach). despite / in spite of + -ing / noun.",
     ["Although it was cold, we walked.", "It was raining; however, we went out.", "Despite the rain, we walked.", "In spite of being tired, she finished the report."]),
    ("Indirect / Embedded questions",
     "W pytaniach pośrednich kolejność jest jak w twierdzeniu (no inversion, no do/does/did). Wprowadzamy: Could you tell me / Do you know / I wonder…",
     ["Could you tell me where the station is?", "Do you know what time it starts?", "I wonder if she is coming.", "Can you tell me how this works?"]),
]

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
def make_quiz(vocab, idioms, grammar):
    """Build 10 quiz questions: 4 vocab-translate (EN->PL), 2 idiom-meaning, 2 fill-in, 2 grammar-pick."""
    qs = []
    # Helper to pick distractors
    pool_pl = [v[3] for v in vocab]
    for i in range(4):
        w = vocab[i]
        # distractors from other vocab
        opts = [w[3]]
        j = 0
        for v in vocab:
            if v[3] != w[3]:
                opts.append(v[3])
                j += 1
            if j >= 3: break
        import random
        random.seed(hash(w[0])%1000)
        random.shuffle(opts)
        qs.append({
            "type": "translate",
            "q": f"Co oznacza słowo „{w[0]}\"?",
            "options": opts,
            "correct": opts.index(w[3]),
            "explain": f"„{w[0]}\" = {w[3]} (np. {w[4]})"
        })
    # idiom meaning
    for i in range(min(2, len(idioms))):
        idm = idioms[i]
        opts = [idm[1]]
        for k in IDIOM_POOL[:6]:
            if k[1] != idm[1] and len(opts) < 4:
                opts.append(k[1])
        import random
        random.seed(hash(idm[0])%1000)
        random.shuffle(opts)
        qs.append({
            "type": "idiom",
            "q": f"Co znaczy idiom „{idm[0]}\"?",
            "options": opts,
            "correct": opts.index(idm[1]),
            "explain": f"„{idm[0]}\" = {idm[1]}"
        })
    # fill-in based on vocab examples
    for i in range(2):
        w = vocab[5+i]
        sentence = w[4].replace(w[0], "_____", 1)
        if "_____" not in sentence:
            sentence = f"I need to _____ this. ({w[3]})"
        opts = [w[0]]
        for v in vocab:
            if v[0] != w[0] and len(opts) < 4:
                opts.append(v[0])
        import random
        random.seed(hash(w[0]+"f")%1000)
        random.shuffle(opts)
        qs.append({
            "type": "fill",
            "q": f"Uzupełnij: „{sentence}\"",
            "options": opts,
            "correct": opts.index(w[0]),
            "explain": f"Pełne zdanie: „{w[4]}\""
        })
    # grammar-based
    g_title, g_rule, g_examples = grammar
    for i, ex in enumerate(g_examples[:2]):
        words = ex.split()
        if len(words) > 4:
            target_idx = len(words) // 2
            target = words[target_idx].strip(".,!?")
            sentence = ex.replace(target, "_____", 1)
            opts = [target]
            distractor_words = [w.strip(".,") for w in ex.split() if w.strip(".,").lower() != target.lower()]
            for d in distractor_words[:3]:
                if d not in opts and len(opts) < 4:
                    opts.append(d)
            while len(opts) < 4:
                opts.append("...")
            import random
            random.seed(hash(ex)%1000)
            random.shuffle(opts)
            qs.append({
                "type": "grammar",
                "q": f"Gramatyka ({g_title}). Uzupełnij: „{sentence}\"",
                "options": opts,
                "correct": opts.index(target),
                "explain": f"Poprawnie: „{ex}\""
            })
    return qs[:10]

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

def topic_extra_dialog(topic_slug):
    """Lightweight second dialog."""
    base = DIALOGS[topic_slug]
    # Reverse speakers / shift
    return [(b[0], b[1], b[2]) for b in base[:4]] + [
        ("A","Anyway, we should continue this later.","W każdym razie powinniśmy do tego wrócić później."),
        ("B","Sounds good. Talk soon!","Brzmi dobrze. Do usłyszenia!"),
    ]

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

OUT = []
OUT.append("""// AUTO-GENERATED by scripts/gen_lessons.py — do not edit by hand.
export interface BuiltinVocab { id: string; en: string; ipa: string; plPron: string; pl: string; example: string; }
export interface BuiltinIdiom { id: string; en: string; pl: string; example: string; }
export interface BuiltinDialogLine { speaker: string; en: string; pl: string; }
export interface BuiltinDialog { lines: BuiltinDialogLine[]; }
export interface BuiltinGrammar { title: string; rule: string; examples: string[]; }
export interface BuiltinQuizQ { q: string; options: string[]; correct: number; explain: string; }
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
  quiz: BuiltinQuizQ[];
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
    extraD = topic_extra_dialog(slug)
    grammar = GRAMMAR_POOL[(n-1) % len(GRAMMAR_POOL)]
    dialog1 = DIALOGS[slug]
    # secondary dialog: trimmed flip
    dialog2 = list(reversed(dialog1[:6]))
    quiz = make_quiz(vocab, idioms, grammar)

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
    OUT.append("quiz:" + quiz_obj(quiz) + ",")
    OUT.append("extraVocab:[" + ",".join(vocab_obj(lid+"-x", i, v) for i, v in enumerate(extraV)) + "],")
    OUT.append("extraIdioms:[" + ",".join(idiom_obj(lid+"-x", i, idm) for i, idm in enumerate(extraI)) + "],")
    OUT.append("extraDialog:" + dlg_obj(extraD) + ",")
    OUT.append("},\n")

OUT.append("];\n")

with open("src/content/lessons.ts", "w", encoding="utf-8") as f:
    f.write("".join(OUT))

print(f"Generated {len(TOPICS)} lessons -> src/content/lessons.ts")
print(f"File size: {os.path.getsize('src/content/lessons.ts')} bytes")
