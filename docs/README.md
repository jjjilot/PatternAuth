# PatternAuth

### Abstract
Multi-factor authentication systems are used by many companies with large user bases to ensure user authentication cannot be bypassed. However, these methods are often susceptible to phishing, SIM swapping, and user fatigue attacks. As a solution to these problems, we created PatternAuth, a robust multi-factor authentication system that seeks to combine the merits of graphical pattern authentication with biometric security and dynamic credential revocation. PatternAuth provides a unique solution by combining three fundamental factors of authentication: something the user knows (graphical patterns and passwords), something the user has (a registered phone), and something the user is (FaceID biometry). By capitalizing on weekly mandatory pattern updates via an iOS app secured with biometric authentication, PatternAuth significantly reduces the time frame of potential attacks such as shoulder surfing or credential theft. The implementation of a security pattern as the primary mode of user authentication was inspired by a study conducted by Sun, Wang, and Zheng el al., which demonstrated that patterns can become very secure as their complexity increases. The purpose of developing PatternAuth was to provide users with an experience that is not only less prone to phishing, stolen credentials, and fatigue for the user themselves, but also allows them to rest assured that their important data remains secure and confidential. The project was evaluated against predetermined user experience evaluation criteria discussed in later sections.

### Manual
The PatternAuth program consists of two user-end installations. To begin, ensure you have navigated to the PatternAuth directory. 

The first installation can be found by navigating to src/website. To initalize the website the dependencies needed are node, npm and npx. Download Node.js onto your machine. If Node.js is downloaded, all three will be installed automatically. You can verify these were downloaded by typing these checks into the terminal. 
```
node -v
npm -v
npx -v
```
To boot up the website cd into the website directory and run these commands. 
``` 
src/website
npm install # (only for first time running website)
npm start
```
The second installation can be found by navigating to src/ios_app. This directory contains a directory with the iOS app source code and a README. To install the iOS app on your phone, you must have access to an iOS device and have downloaded Xcode onto your machine, which requires a MacOS machine. To install the PatternAuth app, connect your Ios device to your machine (through wired connection) and follow the directions in the ios_app README.
