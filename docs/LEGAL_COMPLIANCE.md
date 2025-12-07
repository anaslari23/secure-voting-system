# Legal & Compliance Research (India Context)

## 1. Overview
Implementing online voting in India requires navigating a complex legal framework primarily governed by the **Election Commission of India (ECI)** and the **Representation of the People Act, 1951 (RPA)**.

## 2. Key Legal Provisions

### 2.1 Representation of the People Act, 1951
- **Section 61A**: Empowered the ECI to use **EVMs**.
- **Challenge**: This section specifically mentions "Electronic Voting Machines". Introducing "Online Voting" (remote) would likely require an **Amendment by Parliament** to redefine "recording of votes".
- **Opportunity**: A "Kiosk" model can be legally argued as a "Networked EVM", arguably falling under existing EVM provisions if physically situated in polling stations.

### 2.2 Conduct of Elections Rules, 1961
- **Rule 49**: Governs the voting procedure.
- **Requirement**: Maintaining secrecy of vote (Rule 49M).
- **Impact**: Any system must prove that secrecy is mathematically and physically preserved.

### 2.3 Information Technology Act, 2000
- **Section 43A**: Data privacy and reasonable security practices.
- **Section 66**: Hacking and data theft offences.
- **Relevance**: The backend functionality (Bulletin Board) must comply with CERT-In guidelines for critical information infrastructure.

## 3. Compliance Checklist for Prototype
- [ ] **Data Localization**: All voter data and servers must be physically hosted within India (MeitY requirement).
- [ ] **Source Code Audit**: The ECI requires software to be audited by STQC (Standardisation Testing and Quality Certification).
- [ ] **Transparency**: While EVM code is proprietary, a "Publicly Verifiable" system implies Open Source, which conflicts with current ECI tradition but aligns with modern best practices. **Proposal: Controlled Source Access for Auditors.**

## 4. The "Postal Ballot" Exception
- **ETPBS (Electronically Transmitted Postal Ballot System)** exists for Service Voters.
- **Remote Expansion Strategy**: Initially, frame the "Remote Voting" pilot as an extension of the *Postal Ballot* system for specific classes (NRIs, PwD), rather than general voting, to bypass full Parliamentary amendment requirements for the pilot phase.
