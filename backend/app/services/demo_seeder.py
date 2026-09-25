import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.legal import (
    Page, Chunk, Clause, Party, Obligation, Right, Deadline,
    Restriction, FinancialTerm, Reference, Contradiction, MissingProtection
)
from backend.app.services.security import SecurityService
from backend.app.services.ai_providers import AIProviderFactory

DEMO_USER_ID = "demo-user-lexlens"
DEMO_DOC_ID_V1 = "demo-doc-employment-v1"
DEMO_DOC_ID_V2 = "demo-doc-employment-v2"
DEMO_DOC_ID_LEASE = "demo-doc-commercial-lease"

EMPLOYMENT_V1_TEXT = """EXECUTIVE EMPLOYMENT AGREEMENT

This Executive Employment Agreement (the "Agreement") is entered into as of January 15, 2026, by and between CloudScale Systems, Inc., a Delaware corporation ("Employer" or "Company"), and Alex Mercer ("Employee").

--- Page 1 ---
RECITALS
WHEREAS, Company desires to employ Employee as Principal AI Architect, and Employee desires to accept such employment upon the terms and conditions hereinafter set forth;
NOW, THEREFORE, in consideration of the mutual covenants and promises herein contained, the parties agree as follows:

1. POSITION AND DUTIES
1.1 Position. Employee shall serve as Principal AI Architect, reporting to the Chief Technology Officer. Employee shall perform all duties customary to such position and such other duties as may be assigned from time to time.
1.2 Full-Time Devotion. Employee shall devote Employee's entire productive time, attention, and energies to the business of the Company, and shall not engage in any other business or commercial activity without prior written consent.

2. TERM
2.1 Term. The term of employment shall commence on February 1, 2026 and continue until terminated by either party pursuant to Section 5 or Section 18 herein.

3. COMPENSATION AND BENEFITS
3.1 Base Salary. Company shall pay Employee an initial base salary of $185,000 per annum, payable in accordance with the Company's standard payroll practices, subject to statutory deductions.
3.2 Annual Performance Bonus. Employee shall be eligible for an annual target discretionary bonus of up to twenty percent (20%) of Base Salary, contingent upon achievement of milestones established by the Board.
3.3 Equity Grant. Subject to Board approval, Employee shall be granted options to purchase 50,000 shares of Common Stock, vesting over a four (4) year period with a one-year cliff.

--- Page 2 ---
4. EXPENSE REIMBURSEMENT AND PAYMENTS
4.1 Reimbursement of Expenses. Company shall reimburse Employee for all reasonable and documented business expenses within thirty (30) days of invoice submission and verification.

5. TERMINATION BY COMPANY
5.1 Termination for Cause. Company may terminate Employee's employment immediately without notice for Cause, defined as willful misconduct, gross negligence, fraud, or material breach of this Agreement.
5.2 Termination Without Cause. Company may terminate Employee's employment without Cause upon thirty (30) days prior written notice to Employee.

--- Page 3 ---
12. INTELLECTUAL PROPERTY ASSIGNMENT
12.1 Broad Inventions Assignment. Employee agrees that all inventions, discoveries, designs, software, computer programs, algorithms, models, and improvements created, conceived, or reduced to practice by Employee, solely or jointly with others, during the term of employment, whether or not during normal working hours and whether or not using Company facilities or equipment, shall be the sole and exclusive property of Company.
12.2 Power of Attorney. Employee irrevocably designates and appoints Company and its duly authorized officers as Employee's agent and attorney-in-fact to execute and file all patent and copyright applications.

--- Page 4 ---
14. RESTRICTIVE COVENANTS
14.1 Non-Competition. During employment and for a period of twelve (12) months following termination of employment for any reason, Employee shall not directly or indirectly engage in, manage, operate, consult for, or invest in any business that competes with the enterprise generative AI products of Company within North America.
14.2 Non-Solicitation. For a period of twenty-four (24) months post-termination, Employee shall not solicit or hire any employee or contractor of Company.

--- Page 5 ---
18. RESIGNATION AND NOTICE OBLIGATION
18.1 Voluntary Resignation. Employee may terminate employment by voluntary resignation.
18.2 Extended Notice Requirement. In the event of resignation, Employee shall provide ninety (90) days prior written notice to Company to facilitate comprehensive knowledge transfer and architectural handoff. Failure to provide ninety (90) days written notice shall forfeit accrued unvested equity options and any discretionary bonus.

--- Page 6 ---
22. GOVERNING LAW AND DISPUTE RESOLUTION
22.1 Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflict of laws principles.
22.2 Arbitration. Any controversy or dispute arising out of or relating to this Agreement shall be settled by binding arbitration in Wilmington, Delaware.

--- Page 7 ---
SCHEDULE B: CONSULTING EXPENSES & OVERRIDE TERMS
Notwithstanding Section 4.1, all advanced travel allocations, equipment expenses, and specialized vendor reimbursements submitted under Schedule B shall be approved and paid within sixty (60) days of receipt by Accounts Payable.
"""

EMPLOYMENT_V2_TEXT = """EXECUTIVE EMPLOYMENT AGREEMENT (REVISED COUNTER-OFFER)

This Revised Executive Employment Agreement (the "Agreement") is entered into as of January 22, 2026, by and between CloudScale Systems, Inc. ("Employer") and Alex Mercer ("Employee").

--- Page 1 ---
RECITALS & APPOINTMENT
Employee shall serve as Principal AI Architect with modified terms reflecting agreed commercial adjustments.

1. COMPENSATION
1.1 Base Salary. Increased Base Salary of $195,000 per annum, paid bi-weekly.
1.2 Signing Bonus. One-time signing bonus of $25,000 payable on first payroll.

--- Page 2 ---
4. EXPENSE REIMBURSEMENT
4.1 Harmonized Payment Terms. Company shall reimburse all business expenses, including Schedule B items, within thirty (30) days of receipt.

5. TERMINATION AND NOTICE HARMONIZATION
5.1 Mutual Notice Period. Either party may terminate employment without Cause upon thirty (30) days prior written notice. The prior 90-day resignation notice requirement has been replaced with thirty (30) days mutual notice.

--- Page 3 ---
12. INTELLECTUAL PROPERTY CARVE-OUT
12.1 Pre-Existing Inventions Exclusion. Employee's pre-existing open-source repositories and personal projects listed on Exhibit A are expressly excluded from Company assignment. IP assignment is strictly limited to work created during working hours using Company equipment directly relating to Company products.

--- Page 4 ---
14. RESTRICTIVE COVENANTS
14.1 Narrowed Non-Compete. Non-competition duration reduced to six (6) months, restricted to direct competitors in enterprise AI reasoning engines within a 50-mile radius.

16. LIMITATION OF LIABILITY
16.1 Liability Cap. In no event shall Employee's aggregate liability under this Agreement exceed the total compensation paid to Employee in the preceding six (6) months.
"""

def seed_demo_data(db: Session):
    # 1. Seed or retrieve Demo User
    demo_user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if not demo_user:
        demo_user = User(
            id=DEMO_USER_ID,
            email="demo@lexlens.ai",
            hashed_password=SecurityService.hash_password("DemoLexLens2026!"),
            full_name="Alex Mercer (Demo)",
            is_active=True,
            is_demo=True
        )
        db.add(demo_user)
        db.commit()

    # 2. Check if Demo Doc V1 exists
    doc_v1 = db.query(Document).filter(Document.id == DEMO_DOC_ID_V1).first()
    if not doc_v1:
        doc_v1 = Document(
            id=DEMO_DOC_ID_V1,
            user_id=DEMO_USER_ID,
            title="Senior AI Architect Employment Agreement (v1)",
            filename="CloudScale_Employment_Agreement_v1.pdf",
            file_type="pdf",
            file_path=os.path.join("storage", "CloudScale_Employment_Agreement_v1.pdf"),
            file_size=245800,
            page_count=7,
            document_type="employment_agreement",
            jurisdiction="Delaware",
            language="English",
            status="analyzed",
            summary=(
                "Executive Employment Agreement between CloudScale Systems, Inc. and Alex Mercer for Principal AI Architect. "
                "Specifies $185,000 base salary, 50,000 equity options, 12-month post-employment non-compete across North America, "
                "and broad IP assignment. Contains notable conflicting payment windows and notice requirements requiring clarification."
            )
        )
        db.add(doc_v1)
        db.commit()

        # Seed Pages
        pages_text = EMPLOYMENT_V1_TEXT.split("--- Page ")
        for p_idx, p_text in enumerate(pages_text[1:], start=1):
            cleaned = p_text.split(" ---\n", 1)[-1].strip()
            db.add(Page(id=f"{DEMO_DOC_ID_V1}-p{p_idx}", document_id=DEMO_DOC_ID_V1, page_number=p_idx, text=cleaned))
        db.commit()

        # Seed Parties
        db.add(Party(id=f"{DEMO_DOC_ID_V1}-p1", document_id=DEMO_DOC_ID_V1, name="CloudScale Systems, Inc.", role="Employer", party_type="Corporation"))
        db.add(Party(id=f"{DEMO_DOC_ID_V1}-p2", document_id=DEMO_DOC_ID_V1, name="Alex Mercer", role="Employee", party_type="Individual"))

        # Seed Core Clauses
        c1 = Clause(
            id=f"{DEMO_DOC_ID_V1}-c1",
            document_id=DEMO_DOC_ID_V1,
            clause_number="3.1",
            title="Base Salary",
            text="Company shall pay Employee an initial base salary of $185,000 per annum, payable in accordance with the Company's standard payroll practices, subject to statutory deductions.",
            page_start=1,
            page_end=1,
            category="Compensation",
            plain_explanation="You will receive an annual salary of $185,000 paid through regular company payroll cycles with standard tax deductions.",
            risk_note="Compensation is clearly specified. Ensure payment schedule (bi-weekly vs monthly) is confirmed.",
            questions_to_ask=json.dumps(["When is the first annual salary review scheduled?"])
        )
        c2 = Clause(
            id=f"{DEMO_DOC_ID_V1}-c2",
            document_id=DEMO_DOC_ID_V1,
            clause_number="4.1",
            title="Reimbursement of Expenses",
            text="Company shall reimburse Employee for all reasonable and documented business expenses within thirty (30) days of invoice submission and verification.",
            page_start=2,
            page_end=2,
            category="Payment",
            plain_explanation="The company must pay back legitimate business expense receipts within 30 days of submission.",
            risk_note="Conficts with Schedule B which states 60 days for specialized expenses.",
            questions_to_ask=json.dumps(["Which payment timeframe governs: Clause 4.1 (30 days) or Schedule B (60 days)?"])
        )
        c3 = Clause(
            id=f"{DEMO_DOC_ID_V1}-c3",
            document_id=DEMO_DOC_ID_V1,
            clause_number="5.2",
            title="Termination Without Cause by Company",
            text="Company may terminate Employee's employment without Cause upon thirty (30) days prior written notice to Employee.",
            page_start=2,
            page_end=2,
            category="Termination",
            plain_explanation="The company can let you go for convenience by giving you 30 days advance notice.",
            risk_note="Notice is asymmetric: Company only gives 30 days notice to terminate, but Employee must give 90 days notice to resign.",
            questions_to_ask=json.dumps(["Can severance pay be negotiated in lieu of the 30-day notice period?"])
        )
        c4 = Clause(
            id=f"{DEMO_DOC_ID_V1}-c4",
            document_id=DEMO_DOC_ID_V1,
            clause_number="12.1",
            title="Broad Inventions Assignment",
            text="Employee agrees that all inventions, discoveries, designs, software, computer programs, algorithms, models, and improvements created, conceived, or reduced to practice by Employee, solely or jointly with others, during the term of employment, whether or not during normal working hours and whether or not using Company facilities or equipment, shall be the sole and exclusive property of Company.",
            page_start=3,
            page_end=3,
            category="Intellectual Property",
            plain_explanation="The company claims ownership of everything you invent or build—even in your free time, on your own laptop, outside work hours.",
            risk_note="Unusually aggressive IP assignment without any carve-out for prior personal inventions or open-source repositories.",
            questions_to_ask=json.dumps(["Can we attach an Exhibit A listing pre-existing code repositories and personal hobby projects to exclude them?"])
        )
        c5 = Clause(
            id=f"{DEMO_DOC_ID_V1}-c5",
            document_id=DEMO_DOC_ID_V1,
            clause_number="14.1",
            title="Non-Competition",
            text="During employment and for a period of twelve (12) months following termination of employment for any reason, Employee shall not directly or indirectly engage in, manage, operate, consult for, or invest in any business that competes with the enterprise generative AI products of Company within North America.",
            page_start=4,
            page_end=4,
            category="Non-compete",
            plain_explanation="You are forbidden from working for, consulting with, or investing in any competing AI company across North America for 1 year after leaving.",
            risk_note="Very broad geographic scope (entire continent) and 12-month post-employment duration may restrict future employment.",
            questions_to_ask=json.dumps(["Is this non-compete enforceable under governing state law?", "Can the scope be narrowed to direct named competitors?"])
        )
        c6 = Clause(
            id=f"{DEMO_DOC_ID_V1}-c6",
            document_id=DEMO_DOC_ID_V1,
            clause_number="18.2",
            title="Extended Resignation Notice Requirement",
            text="In the event of resignation, Employee shall provide ninety (90) days prior written notice to Company to facilitate comprehensive knowledge transfer and architectural handoff. Failure to provide ninety (90) days written notice shall forfeit accrued unvested equity options and any discretionary bonus.",
            page_start=5,
            page_end=5,
            category="Notice",
            plain_explanation="If you decide to quit, you must give 90 days (3 months) advance notice, or forfeit your equity and bonus.",
            risk_note="Significant restriction. If a new employer wants you to start in 2 to 4 weeks, this 90-day lock-in could jeopardize new offers.",
            questions_to_ask=json.dumps(["Can the resignation notice period be reduced to the standard 2-4 weeks or matched to the Company's 30-day notice?"])
        )
        c7 = Clause(
            id=f"{DEMO_DOC_ID_V1}-c7",
            document_id=DEMO_DOC_ID_V1,
            clause_number="Schedule B",
            title="Consulting Expenses & Override Terms",
            text="Notwithstanding Section 4.1, all advanced travel allocations, equipment expenses, and specialized vendor reimbursements submitted under Schedule B shall be approved and paid within sixty (60) days of receipt by Accounts Payable.",
            page_start=7,
            page_end=7,
            category="Payment",
            plain_explanation="Specialized expense reimbursements will take up to 60 days to be paid rather than 30 days.",
            risk_note="Directly contradicts Clause 4.1 (30 days vs 60 days).",
            questions_to_ask=json.dumps(["Confirm which reimbursement schedule governs specialized equipment purchases."])
        )
        db.add_all([c1, c2, c3, c4, c5, c6, c7])
        db.commit()

        # Seed Obligations (17 comprehensive obligations)
        obligations_data = [
            ("Employee", "devote entire productive time and energies to Company business", "time and energy", "Full term", None, "1.2", 1),
            ("Employee", "obtain prior written consent before engaging in other commercial activity", "written consent", "Prior to outside activity", None, "1.2", 1),
            ("Company", "pay initial base salary of $185,000 per annum", "salary", "Bi-weekly / monthly payroll", None, "3.1", 1),
            ("Company", "reimburse documented business expenses within 30 days", "expense reimbursement", "Within 30 days of submission", "30 days", "4.1", 2),
            ("Company", "provide thirty (30) days prior written notice for termination without Cause", "written notice", "Prior to termination", "30 days", "5.2", 2),
            ("Employee", "assign all inventions, software, and algorithms created during employment", "intellectual property", "During employment term", None, "12.1", 3),
            ("Employee", "appoint Company as attorney-in-fact for patent filings", "power of attorney", "Upon demand", None, "12.2", 3),
            ("Employee", "refrain from competing with enterprise generative AI products in North America", "non-compete covenant", "12 months post-termination", "12 months", "14.1", 4),
            ("Employee", "refrain from soliciting or hiring Company employees or contractors", "non-solicitation", "24 months post-termination", "24 months", "14.2", 4),
            ("Employee", "provide ninety (90) days prior written notice prior to resignation", "resignation notice", "Prior to resignation", "90 days", "18.2", 5),
            ("Employee", "conduct comprehensive knowledge transfer and architectural handoff", "knowledge transfer", "During resignation notice period", "90 days", "18.2", 5),
            ("Company", "settle disputes through binding arbitration in Wilmington, Delaware", "arbitration dispute resolution", "Upon dispute", None, "22.2", 6),
            ("Company", "pay Schedule B specialized reimbursements within 60 days", "specialized expense reimbursement", "Within 60 days of receipt", "60 days", "Schedule B", 7),
            ("Employee", "maintain confidentiality of proprietary algorithms and customer records", "confidentiality covenant", "Perpetual", None, "10.1", 3),
            ("Employee", "return all Company laptops, tokens, and data upon termination", "property return", "Within 3 business days of exit", "3 days", "16.1", 4),
            ("Company", "grant 50,000 stock options subject to 1-year cliff vesting", "equity option grant", "Subject to Board approval", "1 year cliff", "3.3", 1),
            ("Employee", "certify compliance with Company data security policies annually", "compliance certification", "Annual review", "Annual", "15.1", 4)
        ]
        for idx, (actor, action, target, trig, dl, c_num, page) in enumerate(obligations_data, start=1):
            db.add(Obligation(
                id=f"{DEMO_DOC_ID_V1}-ob{idx}",
                document_id=DEMO_DOC_ID_V1,
                actor=actor,
                action=action,
                target_object=target,
                trigger=trig,
                deadline=dl,
                duration=dl,
                source_clause_number=c_num,
                source_page=page,
                excerpt=f"{actor} shall {action}."
            ))

        # Seed Deadlines (6 key deadlines)
        deadlines_data = [
            ("Resignation Notice Period", "90 days", "Employee voluntary resignation", "Notice", 1, "18.2", 5),
            ("Company Termination Notice", "30 days", "Company termination without cause", "Notice", 2, "5.2", 2),
            ("General Expense Reimbursement", "30 days", "Submission of expense report", "Payment", 3, "4.1", 2),
            ("Schedule B Expense Reimbursement", "60 days", "Receipt by Accounts Payable", "Payment", 4, "Schedule B", 7),
            ("Non-Competition Restrictive Period", "12 months", "Termination of employment", "Restriction", 5, "14.1", 4),
            ("Equity Option One-Year Cliff", "12 months", "Commencement date anniversary", "Vesting", 6, "3.3", 1)
        ]
        for idx, (event, dur, trig, cat, o_idx, c_num, page) in enumerate(deadlines_data, start=1):
            db.add(Deadline(
                id=f"{DEMO_DOC_ID_V1}-dl{idx}",
                document_id=DEMO_DOC_ID_V1,
                event=event,
                duration_or_date=dur,
                triggering_condition=trig,
                category=cat,
                order_index=o_idx,
                source_clause_number=c_num,
                source_page=page
            ))

        # Seed Contradictions (2 Flagship Contradictions)
        db.add(Contradiction(
            id=f"{DEMO_DOC_ID_V1}-ct1",
            document_id=DEMO_DOC_ID_V1,
            title="Conflicting Payment and Reimbursement Timelines",
            clause_a="Clause 4.1",
            text_a="Company shall reimburse Employee for all reasonable and documented business expenses within thirty (30) days of invoice submission and verification.",
            page_a=2,
            clause_b="Schedule B",
            text_b="Notwithstanding Section 4.1, all advanced travel allocations, equipment expenses, and specialized vendor reimbursements submitted under Schedule B shall be approved and paid within sixty (60) days of receipt by Accounts Payable.",
            page_b=7,
            explanation="These provisions specify conflicting payment windows (30 days in Clause 4.1 versus 60 days in Schedule B). The agreement should be reviewed with counsel to determine whether Schedule B supersedes general reimbursement or if an ambiguity exists.",
            severity="Significant"
        ))
        db.add(Contradiction(
            id=f"{DEMO_DOC_ID_V1}-ct2",
            document_id=DEMO_DOC_ID_V1,
            title="Asymmetric Notice Requirements on Termination",
            clause_a="Clause 5.2",
            text_a="Company may terminate Employee's employment without Cause upon thirty (30) days prior written notice to Employee.",
            page_a=2,
            clause_b="Clause 18.2",
            text_b="In the event of resignation, Employee shall provide ninety (90) days prior written notice to Company... Failure to provide ninety (90) days written notice shall forfeit accrued unvested equity options...",
            page_b=5,
            explanation="The agreement establishes starkly asymmetric termination notice periods: Company is only obligated to provide 30 days notice to dismiss Employee, whereas Employee must provide 90 days notice to resign under penalty of forfeiting equity. Counsel should review whether reciprocal 30-day notice can be negotiated.",
            severity="Significant"
        ))

        # Seed Missing Protections
        db.add(MissingProtection(
            id=f"{DEMO_DOC_ID_V1}-mp1",
            document_id=DEMO_DOC_ID_V1,
            protection_type="Pre-Existing IP Carve-Out (Exhibit A)",
            description="Broad intellectual property assignment was identified (Clause 12.1), but no clearly identified carve-out or schedule for pre-existing personal code, open-source repos, or prior inventions was found in the analyzed document.",
            recommendation="Request an Exhibit A (Prior Inventions Schedule) to explicitly exclude your pre-existing projects and open-source contributions from company ownership.",
            severity="High"
        ))
        db.add(MissingProtection(
            id=f"{DEMO_DOC_ID_V1}-mp2",
            document_id=DEMO_DOC_ID_V1,
            protection_type="Limitation of Employee Liability Cap",
            description="No clearly identified liability cap or damages ceiling protecting the employee was found in the analyzed document.",
            recommendation="Confirm with legal counsel whether standard indemnification and a liability ceiling (e.g., capped at 6 months compensation) should be incorporated.",
            severity="Moderate"
        ))

        # Seed Financial Terms
        db.add(FinancialTerm(id=f"{DEMO_DOC_ID_V1}-ft1", document_id=DEMO_DOC_ID_V1, item="Base Salary", amount="$185,000", currency="USD", frequency="Annual", condition="Payable via standard payroll", source_clause_number="3.1"))
        db.add(FinancialTerm(id=f"{DEMO_DOC_ID_V1}-ft2", document_id=DEMO_DOC_ID_V1, item="Target Performance Bonus", amount="20% ($37,000)", currency="USD", frequency="Annual", condition="Contingent on Board milestones", source_clause_number="3.2"))
        db.add(FinancialTerm(id=f"{DEMO_DOC_ID_V1}-ft3", document_id=DEMO_DOC_ID_V1, item="Stock Options", amount="50,000 shares", currency="Shares", frequency="One-time", condition="4-year vesting with 1-year cliff", source_clause_number="3.3"))

        # Seed Chunks with Embeddings
        chunks_data = [
            (1, "Compensation & Role", "3.1", "Company shall pay Employee an initial base salary of $185,000 per annum, payable in accordance with the Company's standard payroll practices."),
            (2, "Expense Reimbursement", "4.1", "Company shall reimburse Employee for all reasonable and documented business expenses within thirty (30) days of invoice submission and verification."),
            (2, "Termination Without Cause", "5.2", "Company may terminate Employee's employment without Cause upon thirty (30) days prior written notice to Employee."),
            (3, "IP Inventions Assignment", "12.1", "Employee agrees that all inventions, discoveries, designs, software, computer programs, algorithms, models, and improvements created, conceived, or reduced to practice by Employee shall be the sole and exclusive property of Company."),
            (4, "Non-Competition", "14.1", "During employment and for twelve (12) months following termination, Employee shall not directly or indirectly engage in or consult for any competing enterprise generative AI business in North America."),
            (5, "Resignation Notice Requirement", "18.2", "In the event of resignation, Employee shall provide ninety (90) days prior written notice to Company to facilitate knowledge transfer. Failure forfeits unvested equity options."),
            (7, "Schedule B Expenses", "Schedule B", "Notwithstanding Section 4.1, all advanced travel allocations, equipment expenses, and specialized vendor reimbursements submitted under Schedule B shall be approved and paid within sixty (60) days.")
        ]
        embed_provider = AIProviderFactory.get_embedding_provider()
        for c_idx, (p_num, sec, c_num, txt) in enumerate(chunks_data, start=1):
            emb = embed_provider.embed_query(txt)
            db.add(Chunk(
                id=f"{DEMO_DOC_ID_V1}-chk{c_idx}",
                document_id=DEMO_DOC_ID_V1,
                page_number=p_num,
                section=sec,
                clause_id=c_num,
                text=txt,
                embedding_json=json.dumps(emb)
            ))

        db.commit()

    # 3. Check if Demo Doc V2 exists (for Instant Contract Comparison Demo)
    doc_v2 = db.query(Document).filter(Document.id == DEMO_DOC_ID_V2).first()
    if not doc_v2:
        doc_v2 = Document(
            id=DEMO_DOC_ID_V2,
            user_id=DEMO_USER_ID,
            title="Senior AI Architect Employment Agreement (v2 - Revised Counter-Offer)",
            filename="CloudScale_Employment_Agreement_v2_Counter.pdf",
            file_type="pdf",
            file_path=os.path.join("storage", "CloudScale_Employment_Agreement_v2_Counter.pdf"),
            file_size=251200,
            page_count=4,
            document_type="employment_agreement",
            jurisdiction="Delaware",
            language="English",
            status="analyzed",
            summary=(
                "Revised counter-offer for Principal AI Architect. Harmonizes payment terms to Net 30 days, reduces resignation notice "
                "from 90 days to 30 days mutual notice, incorporates explicit Pre-Existing IP exclusion, narrows non-compete to 6 months (50 miles), "
                "increases base salary to $195,000, and introduces an employee liability cap."
            )
        )
        db.add(doc_v2)
        db.commit()

        # Seed Pages
        pages_text_v2 = EMPLOYMENT_V2_TEXT.split("--- Page ")
        for p_idx, p_text in enumerate(pages_text_v2[1:], start=1):
            cleaned = p_text.split(" ---\n", 1)[-1].strip()
            db.add(Page(id=f"{DEMO_DOC_ID_V2}-p{p_idx}", document_id=DEMO_DOC_ID_V2, page_number=p_idx, text=cleaned))
        db.commit()

        # Seed Clauses for V2
        c_v2_1 = Clause(id=f"{DEMO_DOC_ID_V2}-c1", document_id=DEMO_DOC_ID_V2, clause_number="1.1", title="Base Salary", text="Increased Base Salary of $195,000 per annum, paid bi-weekly.", page_start=1, page_end=1, category="Compensation", plain_explanation="Increased salary of $195,000.")
        c_v2_2 = Clause(id=f"{DEMO_DOC_ID_V2}-c2", document_id=DEMO_DOC_ID_V2, clause_number="4.1", title="Harmonized Payment Terms", text="Company shall reimburse all business expenses, including Schedule B items, within thirty (30) days of receipt.", page_start=2, page_end=2, category="Payment", plain_explanation="All reimbursements paid in 30 days.")
        c_v2_3 = Clause(id=f"{DEMO_DOC_ID_V2}-c3", document_id=DEMO_DOC_ID_V2, clause_number="5.1", title="Mutual Notice Period", text="Either party may terminate employment without Cause upon thirty (30) days prior written notice. The prior 90-day resignation notice requirement has been replaced with thirty (30) days mutual notice.", page_start=2, page_end=2, category="Notice", plain_explanation="Fair 30 days mutual notice for both sides.")
        c_v2_4 = Clause(id=f"{DEMO_DOC_ID_V2}-c4", document_id=DEMO_DOC_ID_V2, clause_number="12.1", title="Pre-Existing Inventions Exclusion", text="Employee's pre-existing open-source repositories and personal projects listed on Exhibit A are expressly excluded from Company assignment.", page_start=3, page_end=3, category="Intellectual Property", plain_explanation="Protects your personal projects from company takeover.")
        c_v2_5 = Clause(id=f"{DEMO_DOC_ID_V2}-c5", document_id=DEMO_DOC_ID_V2, clause_number="16.1", title="Liability Cap", text="In no event shall Employee's aggregate liability under this Agreement exceed the total compensation paid to Employee in the preceding six (6) months.", page_start=4, page_end=4, category="Liability", plain_explanation="Caps your potential liability to 6 months pay.")
        db.add_all([c_v2_1, c_v2_2, c_v2_3, c_v2_4, c_v2_5])
        db.commit()
