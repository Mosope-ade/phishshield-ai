# PhishShield AI

PhishShield AI is a free, public, privacy-first decision-support platform designed to protect users from social engineering attacks by detecting phishing and scams instantly. The application is built for general public use, requiring no user accounts, no login, and storing no personal data.

Users can submit suspicious messages, URLs, screenshots of messages/emails, or QR codes. The platform processes the input, aggregates multi-layered security indicators, and explains its reasoning in clear, plain language.

---

## The Three-Layer Detection Architecture

A core design law of PhishShield AI is that no single layer of evidence ever silently overrides another. Every report displays findings separately by their source so that users can make informed security decisions.

### 1. Deterministic Heuristics Layer (Uninjectable)
The first layer runs entirely server-side without external network calls. Because it is deterministic, it cannot be bypassed or fooled by adversarial text instructions (prompt injections). It checks for:
- **Typosquatting & Homoglyphs**: Calculates edit distances (Levenshtein ≤ 2) against the top 1M domains and flags Unicode substitutions that spoof popular brand domains.
- **Brand Subdomain Impersonation**: Flags when trusted brand names appear in subdomains of untrusted registered domains (e.g., `paypal.com.login-verify.ru`).
- **TLD & URL Features**: Identifies suspicious top-level domains commonly used in phishing, excessive URL length, known shorteners, HTTP connections, and credential-harvesting keywords.

### 2. Large Language Model (LLM) Layer
A Large Language Model analyzes the semantic intent of messages, images, and page content.
- **Social Engineering Markers**: Inspects text for urgency, fear tactics, payment requests, unrealistic rewards, or tone inconsistencies.
- **Prompt-Injection Defense**: Delimits user-influenced input safely and explicitly instructs the model to treat content as data, never as commands.
- **Pydantic Validation**: All raw outputs from the LLM are strictly validated against a server-side schema before ingestion.

### 3. VirusTotal Reputation Layer
Integrates VirusTotal's public registry to check domains and file hashes against 70+ antivirus engines.
- **Corroborating Evidence**: VirusTotal is treated as supportive data — a "clean" result does not suppress strong flags raised by heuristics or AI, preventing newly registered phishing campaigns from bypassing detection.

---

## Core Product Features

- **Unified Submission Surface**: A single interface that automatically detects input types. Paste text, paste a URL, or drop an image. No manual mode selectors.
- **QR Code & Screenshot Processing**: Decodes QR codes ("quishing" protection) and falls back to OCR text extraction for screenshots, passing the payloads through the full analysis pipeline.
- **File Hash Lookup**: Computes SHA-256 hashes of files on upload to query VirusTotal reputations without ever storing or uploading the raw file content.
- **Privacy-First Cache**: Analysis results are cached for up to 24 hours using only SHA-256 hashes of normalized inputs. Raw user submissions are never persisted.
- **Verdict-First User Interface**: Visual presentation displaying a clear threat badge (Low, Medium, High, Critical) and plain-language summary, followed by granular evidence panels and safety recommendations.
- **Security-Minded Permalinks**: Analysis reports can be shared via non-sequential, randomly generated slug URLs. All report pages are marked `noindex` to keep search engines from indexing them.
