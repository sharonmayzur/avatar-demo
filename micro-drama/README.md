# Micro Drama – React Native (Expo)

A vertical micro-drama streaming app for mobile.

## Setup

```bash
# Install Node.js first (if not installed):
# https://nodejs.org  or  brew install node

cd micro-drama
npm install
npx expo start
```

Then scan the QR code with the **Expo Go** app on your phone, or press `i` for iOS simulator / `a` for Android emulator.

## Screens

### Home Screen
- Dark themed content rails (Crime, New Episodes, Portrait, My Recordings)
- Tap any card to open the full-screen player

### Player Screen
- Full-screen vertical video
- **Tap the screen** → hides all overlay UI (only progress bar + episode info remain)
- **Tap again** → restores full overlay (back button, like/comment/share, title)
- Back arrow (top left) → returns to Home

## Project Structure

```
App.js                        # Root with navigation
src/
  data/mockData.js            # Shows and rails data
  screens/
    HomeScreen.js             # Asset list with rails
    PlayerScreen.js           # Full-screen episode player
  components/
    ContentCard.js            # Single content thumbnail card
    ContentRail.js            # Horizontal scrollable rail
```
