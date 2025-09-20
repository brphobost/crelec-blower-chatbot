# Deployment Guide - Vercel (FREE)

## Step 1: Prepare Repository

1. Push this project to a GitHub repository
2. Make sure all files are committed

## Step 2: Deploy to Vercel

### Option A: Using Vercel CLI (Fastest)

```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# In the project root directory
vercel

# Follow prompts:
# - Link to existing project? No
# - What's your project name? crelec-blower-chat
# - Which directory? ./ (current directory)
# - Override settings? No
```

### Option B: Using Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Import your GitHub repository
4. **IMPORTANT**: Set root directory to `./` (the blower-chatbot folder)
5. Framework Preset: "Other"
6. Build settings will auto-detect from vercel.json
7. Click "Deploy"

## Step 3: Update Widget URL

After deployment, you'll get a URL like: `https://crelec-blower-chat.vercel.app`

Update this in:
1. `deploy/widget-embed.js` - Change WIDGET_URL
2. `deploy/embed-snippet.html` - Update the example URLs

## Step 4: Test Your Deployment

1. Visit: `https://your-app.vercel.app` - Main chat interface
2. Visit: `https://your-app.vercel.app/api` - Should return API status
3. Test widget embedding with this HTML:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Widget Test</title>
</head>
<body>
    <h1>My Website</h1>
    <p>Testing Crelec widget...</p>

    <script>
    (function() {
        var script = document.createElement('script');
        script.src = 'https://your-app.vercel.app/widget-embed.js';
        script.async = true;
        document.body.appendChild(script);
    })();
    </script>
</body>
</html>
```

## Step 5: Share with Customer

Give your customer:
1. **Direct Link**: `https://your-app.vercel.app`
2. **Embed Code** for their website:

```html
<script>
(function() {
    var script = document.createElement('script');
    script.src = 'https://your-app.vercel.app/widget-embed.js';
    script.async = true;
    document.body.appendChild(script);
})();
</script>
```

## Vercel Free Tier Limits

✅ **What's Included FREE:**
- 100GB bandwidth/month (plenty for testing)
- Serverless Functions (Python API)
- Custom domains (if you have one)
- HTTPS/SSL included
- Automatic deployments from Git

❌ **Limitations:**
- 10 second timeout for API calls
- No persistent storage (use Supabase if needed)
- Sessions reset after inactivity

## Optional: Add Persistence with Supabase

If you want to save quotes permanently:

1. Create a Supabase project (FREE tier)
2. Create tables for quotes and conversations
3. Add Supabase client to backend
4. Update API to save/retrieve from Supabase

But for testing, the in-memory storage works fine!

## Troubleshooting

**Issue**: API not working
- Check Vercel Functions logs in dashboard
- Make sure calculator.py is in backend/api/

**Issue**: CORS errors
- Already handled in the code
- If issues persist, check browser console

**Issue**: Widget not appearing
- Check that widget-embed.js URL is correct
- Check browser console for errors

## Custom Domain (Optional)

1. In Vercel dashboard → Settings → Domains
2. Add your domain (e.g., chat.crelec.co.za)
3. Update DNS records as instructed
4. Update widget-embed.js with new domain

---

That's it! Your chatbot is now live and can be embedded on any website!