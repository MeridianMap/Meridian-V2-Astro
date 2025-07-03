# Authentication Setup for Meridian V2.1

## Simple Password Authentication

This branch implements a simple password-based authentication system for Meridian.

### Configuration

Add these environment variables to your frontend `.env` file:

```env
# Authentication Settings
VITE_ACCESS_PASSWORD=explore
VITE_REQUIRE_AUTH=true
```

### Features

- **Password Protection**: Users must enter the correct password to access the application
- **Session Persistence**: Authentication state is saved in session storage (until browser is closed)
- **Logout Functionality**: Users can logout via a button in the top-right corner
- **Development Toggle**: Set `VITE_REQUIRE_AUTH=false` to disable auth during development
- **Docker Support**: Environment variables are already configured in Dockerfile

### Usage

1. **Enable Authentication**: Set `VITE_REQUIRE_AUTH=true` in your `.env` file
2. **Set Password**: Set `VITE_ACCESS_PASSWORD=your_password` in your `.env` file
3. **Access Application**: Users will see a password prompt before entering the app
4. **Default Password**: Currently set to "explore"

### Security Notes

- This is a **frontend-only** authentication system suitable for basic access control
- The password is stored in environment variables and checked client-side
- For production use, consider implementing backend authentication for stronger security
- Session storage clears when the browser is closed, requiring re-authentication

### Testing

```bash
# Run with authentication enabled
npm run dev

# Run without authentication (development)
VITE_REQUIRE_AUTH=false npm run dev
```

The authentication screen features a modern gradient design matching the Meridian brand.
