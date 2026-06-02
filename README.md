# Naukri Job Apply Autobot

Yeh ek automated bot hai jo **Playwright (Python)** ka use karke Naukri.com par **Full Stack Developer (Fresher)** jobs ko automatically search aur apply karta hai.

---

## 🛠️ Requirements & Setup

Sabse pehle aapko is project ko chalane ke liye Python aur Playwright setup karna hoga.

### 1. Dependencies Install karein
Apne terminal mein is `autobot` folder ke andar jayein aur yeh commands run karein:
```powershell
# 1. Directory mein jayein
cd d:\fclone\portal\src\pages\WelcomePage\parts\automationtest\autobot

# 2. Required Python packages install karein
pip install -r requirements.txt

# 3. Playwright browser download karein
playwright install
```

### 2. `.env` File Check karein
Project folder ke andar `.env` file automatically bani huyi hai jisme aapke credentials hain:
```env
NAUKRI_EMAIL=dummy@gmail.com
NAUKRI_PASSWORD=847201
```
*Note: Agar aapko kabhi email ya password change karna ho, toh aap is `.env` file ko open karke credentials badal sakte hain.*

---

## 🚀 Bot ko Kaise Chalayein?

Bot ko chalane ke do simple steps hain:

### Step 1: Login Session Setup (Sirf Ek Baar)
Pehle hamein browser session save karna hoga taaki Naukri aapko bot samajh kar block na kare aur Captcha/OTP manually bypass ho sake.

```powershell
python setup_session.py
```
* **Kya hoga**: Ek Chromium browser window open hogi.
* **Aapko kya karna hai**: Credentials automatic fill ho jayenge. Agar koi **Captcha** aata hai toh solve karein, aur **Login** click karein. Dashboard khulne ke baad **browser window ko close (X) kar dein**.
* **Result**: Aapka session `naukri_session/` folder mein save ho jayega.

---

### Step 2: Auto Apply Bot Chalayein
Session save hone ke baad aap auto-apply script ko chala sakte hain:

```powershell
python naukri_bot.py
```
* **Kya hoga**: 
  1. Browser open hoga aur check karega ki aap logged in hain ya nahi.
  2. Agar login nahi hain, toh automatic login karega.
  3. Dashboard par scroll karke top par search box par jayega.
  4. Search box mein click karke type karega: `Full Stack Developer fresher` aur Enter press karega.
  5. Search results aane par, left-side ya notification modals ko close karega.
  6. Ek-ek karke jobs ke Title par click karega aur new tab mein check karega ki **Apply** button hai ya nahi.
  7. Direct apply button hone par apply karega aur external sites ko skip kar dega.
  8. Har page scan hone ke baad automatically bottom par **Next** button click karke agle page par badhega.

---

## ⚠️ Important Tips (⚠️ Zaroori Baatein)

1. **Popup Questionnaire**: Kabhi-kabhi apply button click karne par "Notice Period" ya "Expected CTC" ka popup screen par aa jata hai. Bot wahan warning print karega aur 5-10 second wait karega taaki agar aap dekh rahe hain toh use select kar dein.
2. **Speed & Blocking**: Bot ke andar natural insani behavior (random delay 2 to 8 seconds) daala gaya hai taaki Naukri aapka account block na kare. Ise poore din continuously na chalayein.
3. **External Apply**: Kuch jobs direct Naukri par apply nahi hoti, balki company ki career page par redirect karti hain. Bot aisi external links ko skip kar deta hai kyuki unke forms alag hote hain.
