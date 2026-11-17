"""Knowledge base: answers to student doubts + guided form help. Edit freely: add entries to KB."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

NSP = "https://scholarships.gov.in/"
OTR = "https://scholarships.gov.in/otrapplication/#/"
OTRAPP = "https://play.google.com/store/apps/details?id=in.gov.scholarships.nspotr"
FACERD = "https://play.google.com/store/apps/details?id=in.gov.uidai.facerd"
L_NSP, L_OTR = {"label": "Open NSP portal", "url": NSP}, {"label": "Generate OTR", "url": OTR}

KB = [
 {"q": ["what is otr", "one time registration", "what is otr id", "otr meaning"],
  "a": "OTR (One Time Registration) is a unique 14-digit ID you create once on NSP using your Aadhaar. It stays valid for your whole academic career, and you need it before applying to any scheme. Only one OTR is allowed per student.", "links": [L_OTR]},
 {"q": ["how to generate otr", "create otr", "otr registration steps", "otr face authentication", "otr app", "register on nsp", "nsp registration"],
  "a": "How to make your OTR:\n1. Open scholarships.gov.in and choose Get your OTR.\n2. Enter your mobile number and verify the OTP.\n3. Enter your Aadhaar number and verify the OTP sent to your Aadhaar-linked mobile.\n4. Add your parents' names and your email. You get a temporary reference number.\n5. Finish with Aadhaar face authentication using the NSP OTR app and the AadhaarFaceRD app (Android, from Google Play).",
  "links": [L_OTR, {"label": "NSP OTR app", "url": OTRAPP}, {"label": "AadhaarFaceRD app", "url": FACERD}]},
 {"q": ["i do not have aadhaar", "aadhaar not available", "aadhaar enrollment id", "no aadhaar card"],
  "a": "OTR can be made with an Aadhaar number or an Aadhaar Enrolment ID (EID). If you have neither, enrol for Aadhaar at an Aadhaar centre first."},
 {"q": ["mobile not linked to aadhaar", "otp not coming", "aadhaar mobile number different", "otp problem", "otp not received"],
  "a": "The Aadhaar OTP goes only to the mobile number linked to your Aadhaar. If that number is old or missing, update it at an Aadhaar Seva Kendra, then retry. If the number is right, check your signal and wait a few minutes before requesting again."},
 {"q": ["how to fill the form", "help me fill application form", "scholarship form steps", "fill nsp form", "application steps", "how to apply", "apply online steps", "application process"],
  "a": "Applying on NSP, step by step:\n1. Make your OTR (once).\n2. Student login. New students pick their domicile state and Fresh. Returning students pick Renewal.\n3. Fill the five tabs: Personal, Academic, Scheme, Bank, Contact.\n4. After the Personal tab you get a TEMPID. Use it with your date of birth to finish the other tabs.\n5. Submit. You get a permanent registration ID (PRID). Save it.\n6. Your institute verifies your application, then state officials do.\nTell me a tab name (for example \"bank details\") and I will explain what to fill.", "links": [L_NSP]},
 {"q": ["personal details tab", "what to fill in personal details", "name date of birth", "father name mother name", "personal tab"],
  "a": "Personal tab: enter your name and date of birth exactly as on your Aadhaar, then gender, category, parents' names, family income and disability status if it applies. Any mismatch with your documents can cause rejection. When you save this tab you get your TEMPID."},
 {"q": ["academic details tab", "course details", "institute name", "aishe code", "previous marks", "admission year", "academic tab"],
  "a": "Academic tab: pick your course, year of study and institute. If you cannot find your institute, search by its AISHE code (ask your college office). Enter your previous exam marks or percentage from your marksheet and your admission details."},
 {"q": ["scheme details tab", "which scheme to select", "choose scholarship scheme", "select scheme", "scheme tab"],
  "a": "Scheme tab: choose the scheme that matches your category, course level and income. Use the Matches panel here to see which ones you qualify for, and only pick those. Choosing a scheme you don't qualify for is a common reason for rejection."},
 {"q": ["bank details tab", "bank account for scholarship", "ifsc", "aadhaar seeding", "account linked to aadhaar", "bank tab"],
  "a": "Bank tab: use an account in your own name, linked (seeded) to your Aadhaar so the money can be paid by direct transfer. Enter the account number and IFSC exactly as on your passbook. Check the account holder name matches your Aadhaar name."},
 {"q": ["contact details tab", "address details", "pin code district", "email mobile", "contact tab"],
  "a": "Contact tab: enter your permanent address with district and pin code, plus a mobile number and email you actually use. Verification messages and updates come here."},
 {"q": ["what is temp id", "tempid", "temporary id", "what is prid", "permanent registration id", "track application status", "application status"],
  "a": "TEMPID is a temporary ID you get after saving the Personal tab. Use it with your date of birth to finish the remaining tabs. After you submit, you get a PRID (permanent registration ID). Use the PRID to track your application status and to renew next year. Keep both safe.", "links": [L_NSP]},
 {"q": ["institute verification", "college verification", "who verifies application", "verification pending", "hard copy submit", "submit documents to college"],
  "a": "After you submit, your institute checks your application on the portal, then district or state officials verify it. Take your documents (and a printout if your college asks) to the college scholarship office. If it stays pending, ask the college nodal officer to complete verification."},
 {"q": ["last date nsp 2026", "when does nsp close", "when to apply", "application window", "nsp open date", "closing date"],
  "a": "NSP opened for 2026-27 on 1 June 2026. Third-party listings report 31 October 2026 as the last date for most schemes, but dates differ by scheme and verification deadlines come after that. Apply by September to stay safe and confirm on the portal.", "links": [L_NSP]},
 {"q": ["documents required", "what documents do i need", "certificates needed", "papers to apply", "documents for nsp"],
  "a": "Usual documents: Aadhaar card, bank passbook (Aadhaar-linked, your name), income certificate, previous marksheet, admission or institute ID proof, passport photo. Add a caste certificate for SC/ST/OBC, a minority declaration for minority schemes, or a disability certificate (40% or more) if it applies. Ask me about a specific scheme for its exact list."},
 {"q": ["income certificate", "how to get income certificate", "which income counts", "parents income", "family income"],
  "a": "The income certificate is issued by your state's competent revenue authority (often the tehsildar or the state e-district portal). It should be current and show total family income from all sources. It must be within the scheme's limit."},
 {"q": ["caste certificate", "how to get caste certificate", "obc certificate", "sc st certificate", "non creamy layer"],
  "a": "Caste certificates are issued by your state's competent authority (usually via the tehsildar office or e-district portal). Use a valid, current one in your state's format. OBC schemes may ask for a current certificate, so check the scheme rules."},
 {"q": ["can i apply for more than one scholarship", "two scholarships", "multiple scholarships", "apply for many schemes"],
  "a": "It depends on the scheme. Many central schemes don't allow you to take two scholarships for the same course, so read each scheme's guidelines before applying to more than one. When in doubt, ask your institute's nodal officer."},
 {"q": ["renewal", "renew scholarship", "apply again next year", "renewal process"],
  "a": "To renew, log in as a student and choose Renewal. Update your qualification and other details such as income if needed, then submit. Use your PRID to track it.", "links": [L_NSP]},
 {"q": ["application rejected", "why rejected", "scholarship rejected", "defect", "fix rejection", "returned application"],
  "a": "Common reasons: family income above the scheme limit, name or bank details not matching Aadhaar, Aadhaar-unlinked bank account, wrong scheme chosen, missing documents, or the institute did not verify in time. Check the remark on your application status, fix the issue and, if allowed, resubmit through your institute."},
 {"q": ["edit form after submit", "made mistake in form", "change details", "correct wrong details", "wrong information"],
  "a": "You can edit details before final submission. After final submit, changes usually need your institute to return the application to you, so contact the college nodal officer quickly. Check the portal for the current rule."},
 {"q": ["is nsp free", "fees to apply", "agent", "pay money", "fake website", "cyber cafe charges"],
  "a": "Applying on NSP is free. Only use scholarships.gov.in. Never pay an agent to 'guarantee' a scholarship, and never share your OTP with anyone.", "links": [L_NSP]},
 {"q": ["who is eligible", "basic eligibility for nsp", "eligibility conditions", "nsp eligibility"],
  "a": "General conditions: Indian citizen, enrolled in a recognised institution, family income within the scheme limit, the right category certificate where needed, and an Aadhaar-linked bank account. Each scheme adds its own marks, level and state rules. Tell me your details and I will check every scheme."},
 {"q": ["when will i get money", "scholarship payment", "money not received", "dbt status", "payment not credited"],
  "a": "Payment is sent by direct bank transfer after your application is verified and sanctioned, so timing varies by scheme and state. Check your application status with your PRID and make sure your bank account is Aadhaar-linked. If verified but unpaid for long, raise it with your institute and the portal helpdesk.", "links": [L_NSP]},
 {"q": ["domicile state", "which state to select", "fresh or renewal", "fresh application"],
  "a": "At student login, new applicants select their domicile state (the state you are a permanent resident of) and then Fresh. If you applied before, choose Renewal."},
 {"q": ["helpline", "contact nsp", "support number", "complaint", "grievance", "help desk"],
  "a": "Use the Helpdesk / Contact Us section on scholarships.gov.in for the current helpline and email, and speak to your institute's nodal officer for verification problems.", "links": [L_NSP]},
 {"q": ["which scholarship is best", "best scholarship for me", "highest amount scholarship"],
  "a": "The best one is the highest-benefit scheme you actually qualify for. Look at the Eligible list in the Matches panel and compare the amounts and deadlines. Check each scheme's rules on whether you can take more than one."},
 {"q": ["state scholarship", "state government scholarship", "my state scheme"],
  "a": "NSP also hosts some state schemes, and you select your domicile state at login. My database covers central schemes, so check your state's scholarship portal or the NSP state list for state-specific ones."},
]
FORM_GUIDE = [
 {"title": "1. Generate your OTR", "steps": ["Open NSP and choose Get your OTR.", "Verify your mobile, then your Aadhaar OTP.", "Complete face authentication in the NSP OTR app."], "tip": "Do this once. It works for your whole academic career.", "link": L_OTR},
 {"title": "2. Student login", "steps": ["Log in with your OTR.", "New students: choose domicile state, then Fresh.", "Returning students: choose Renewal."], "tip": "Pick the state you permanently live in.", "link": L_NSP},
 {"title": "3. Personal tab", "steps": ["Name and date of birth exactly as on Aadhaar.", "Gender, category, parents' names.", "Family income and disability status."], "tip": "You get a TEMPID after saving. Write it down."},
 {"title": "4. Academic tab", "steps": ["Course, year and institute (search by AISHE code).", "Previous exam marks or percentage.", "Admission details."], "tip": "Copy marks from your marksheet, not from memory."},
 {"title": "5. Scheme tab", "steps": ["Choose the scheme that matches your category, level and income.", "Check the Matches panel first."], "tip": "Only select schemes you qualify for."},
 {"title": "6. Bank tab", "steps": ["Account in your own name.", "Correct account number and IFSC.", "Account linked to Aadhaar."], "tip": "Your name must match your Aadhaar."},
 {"title": "7. Contact tab", "steps": ["Permanent address, district, pin code.", "Mobile and email you use."], "tip": "Updates and verification messages go here."},
 {"title": "8. Submit and follow up", "steps": ["Upload documents and submit.", "Save your PRID.", "Take documents to your college for verification.", "Track status with the PRID."], "tip": "Apply by September. The last date for most schemes is reported as 31 October 2026.", "link": L_NSP},
]

class KnowledgeBase:
    def __init__(self):
        self.txt, self.idx = [], []
        for i, e in enumerate(KB):
            for q in e["q"]: self.txt.append(q); self.idx.append(i)
        self.v = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)); self.m = self.v.fit_transform(self.txt)
    def find(self, text):
        sims = cosine_similarity(self.v.transform([text.lower()]), self.m)[0]
        j = sims.argmax()
        return (KB[self.idx[j]], float(sims[j])) if sims[j] > 0 else (None, 0.0)
