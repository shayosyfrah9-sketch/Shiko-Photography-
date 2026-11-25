# הוראות להקמת Preview עצמאי (לא הוקם, ממתין לאישור)

**מטרה:** להריץ את אבטיפוס הטכנולוגיה כדף רגיל בדפדפן, מחוץ ל־Artifact, כדי למדוד טעינה וביצועים ללא ה־CSP, בלי תחליף הסיומות וללא הגבלות ארגז החול.
**עיקרון מחייב:** ריפו **נפרד וחדש**. שום שינוי ב־Shiko-Photography, ב־main, בענפי הגיבוי, ב־Pages של האתר, בדומיין או בכללי ההגנה.

## מה אני כבר הכנתי (בלי לגעת בשום הגדרה)
`node studio/village/techproof/make-preview.mjs` בונה תיקייה `preview-dist/` מוכנה: מסמך HTML מלא (עם `noindex`), `robots.txt` שחוסם אינדוקס, `.nojekyll`, נכסים ו־transcoder. התיקייה לא נכנסת ל־git (ב־.gitignore). בדקתי שהיא נבנית, וגודלה מדווח בסוף הדוח.

## מה אתה צריך לעשות (כ־5 דקות)
1. GitHub ← New repository. שם מוצע: `shiko-world2-preview`. **Public** (נדרש ל־Pages חינמי; אין בו שום תוכן רגיש: גיאומטריה ניטרלית ו־3 תמונות בגודל ווב). אל תוסיף README/.gitignore.
2. העלה את תוכן `preview-dist/` לשורש הריפו הזה (Add file ← Upload files, או `git push` אם אתה מעדיף). אפשר לקבל אותי לבנות לך ZIP.
3. Settings ← Pages ← Source: **Deploy from a branch**, Branch: **main**, Folder: **/ (root)**. **בלי** Custom domain.
4. אחרי כדקה הכתובת תהיה `https://<המשתמש-שלך>.github.io/shiko-world2-preview/`. שלח לי אותה, או פתח אותה בעצמך בטלפון, במחשב ובאייפון.
5. בדף: בדיקת ביצועים ← העתק תוצאות.

## אפשרות חלופית ללא GitHub
Netlify Drop או Cloudflare Pages: גרור את `preview-dist/`. אותו עיקרון, כתובת נפרדת, בלי דומיין.

## מה זה לא עושה
- לא נוגע ב־shikophotography.com ולא בריפו של האתר.
- אין Actions ואין פריסה אוטומטית.
- להסרה: מחיקת הריפו החדש, או Settings ← Pages ← Unpublish.

## הערה על מדידה
מחוץ ל־Artifact אין תחליף `.png` לקבצי KTX2/GLB, אבל הקוד משתמש באותם שמות, והם מוגשים שם כ־image/png (תקין ל־fetch). תמונות AVIF/WebP מוגשות בסיומת האמיתית.
