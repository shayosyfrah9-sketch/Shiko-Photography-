# הגנה על v153 — מה נבדק ומה צריך לעשות ידנית ב־GitHub (2026-11-25)

## נבדק בפועל
| נושא | מצב | איך נבדק |
|---|---|---|
| main, backup-v153-live, stage6-candidate | כולם = 775a28d | GitHub API |
| גיבוי ענף מוקדם | backup-v146-live = 8274bb0 | GitHub API |
| גיבוי קובץ | `/mnt/project-files/shiko-site/backup-v153-live/v153.bundle` (165 MB) | `git bundle verify` + שחזור בפועל: clone מה־bundle, checkout, עץ הקבצים זהה (hash `e82530c7…`) ל־775a28d, `fsck` נקי |
| תגית v153-live | קיימת רק מקומית. **הדחיפה נכשלה (HTTP 403 מהפרוקסי של הסביבה)**, אין לי כלי ליצירת תגית ב־GitHub | `git push` + `list_tags` (ריק) |
| הגנת ענפים | **אין** (`protected:false` בכל הענפים) | GitHub API |
| פריסה אוטומטית | אין `.github/workflows` בענפים main ו־world2-dev, כלומר אין Action שמפרסם | בדיקת קבצים |
| הוק מקומי | קיים, אבל מקומי בלבד ולא נחשב הגנה | בדיקה מקומית |
| הגדרות Pages | **לא ניתן לבדוק מכאן** | אין גישת API |

## מה אתה צריך לעשות ב־GitHub (כ־5 דקות, בריפו Shiko-Photography-)
### 1. תגית קבועה לגרסה 153
Releases ← Draft a new release ← Choose a tag ← הקלד `v153-live` ← Create new tag on publish. ב־Target בחר **Commit** והדבק `775a28d8981cc4f610fc20ee5967568d3694be31`. כותרת: `v153 live baseline`. סמן Set as the latest release ← Publish release. (יצירת Release יוצרת את התגית.)

### 2. כלל הגנה על התגית
Settings ← Rules ← Rulesets ← New ruleset ← New tag ruleset. שם: `protect v153 tag`. Enforcement: Active. Target tags: Include by pattern `v153-live`. סמן: **Restrict deletions** ו־**Block force pushes**. Bypass list: ריק. ← Create.

### 3. כלל הגנה על main ועל ענפי הגיבוי
Settings ← Rules ← Rulesets ← New ruleset ← New branch ruleset. שם: `protect live and backups`. Enforcement: Active. Target branches ← Add target ← Include by pattern: הוסף `main`, `backup-*`, `stage6-candidate`. סמן:
- **Restrict deletions**
- **Block force pushes**
- **Require a pull request before merging** (כך אי אפשר לדחוף ישירות ל־main; אפשר 0 מאשרים נדרשים)
- Bypass list: ריק. (אם תרצה בעתיד לפרוס, תצטרך למזג PR מתוך world2-dev, וזו בדיוק הפעולה המכוונת.)
הערה: אם חלק מההגדרות לא זמינות, ייתכן שהריפו פרטי. Pages בחינם דורש ריפו ציבורי, ולכן ככל הנראה זה זמין.

### 4. בדיקת Pages (ושליחת צילום מסך אליי)
Settings ← Pages. ודא:
- Source = **Deploy from a branch**, Branch = **main**, Folder = **/ (root)**. אם כתוב ענף אחר, אל תשנה ושלח לי צילום.
- Custom domain = `shikophotography.com`, Enforce HTTPS מסומן.
Settings ← Environments ← github-pages ← Deployment branches: מומלץ **Selected branches: main** בלבד.

## למה הסביבה החדשה לא יכולה לפרוס לדומיין
- תצוגת הניסוי תהיה **Artifact בענן** (כתובת claude.ai נפרדת), לא GitHub Pages.
- הקוד ב־world2-dev נדחף רק לענף הזה. הדומיין מוגש מ־main בלבד (אם Pages מוגדר כנדרש, סעיף 4).
- אין Actions שמפרסמים. אחרי סעיפים 2–4, גם דחיפה בטעות ל־main תיחסם.
- סיכון שנשאר: אם מישהו ישנה את מקור Pages לענף world2-dev, הענף יתפרסם (קובץ CNAME קיים גם בו). לכן סעיף 4.
- **אני לא נוגע בהגדרות GitHub, בלי הרשאה לכך ובלי כוונה.**

## שחזור חירום
```
git clone https://github.com/shayosyfrah9-sketch/Shiko-Photography-.git
git checkout v153-live        # אחרי שהתגית נוצרה
# או בלי GitHub:
git clone /path/to/v153.bundle restore && cd restore && git checkout backup-v153-live
```
