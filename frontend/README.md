# LMS Frontend

This directory contains a very simple React application that demonstrates how you might structure a frontend for the Learning Management System.  It provides pages for logging in, listing courses, and viewing a course detail.  To keep things lightweight and framework‑agnostic, it does not rely on Create React App.  You can integrate these components into your preferred build tool (e.g. Vite, CRA, Next.js) or use a minimal webpack setup.

## Structure

```
src/
├── App.js           # Application root with routing
├── index.js         # Entry point
├── services/
│   └── api.js       # Axios API helper
├── components/
│   └── NavBar.js    # Navigation bar component
└── pages/
    ├── Login.js     # Login page
    ├── Courses.js   # Course list page
    └── CourseDetail.js # Individual course page
public/
└── index.html       # HTML template
package.json         # Dependencies and scripts
```

## Getting Started

1. Ensure you have Node.js and npm installed.
2. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```
3. Start a development server with your chosen bundler.  For example, if you choose Vite:

   ```bash
   npm install vite --save-dev
   npx vite
   ```

   Or if you prefer Create React App:

   ```bash
   npx create-react-app .
   # Then copy the contents of the src/ and public/ folders over the generated ones.
   npm start
   ```

4. The frontend expects the backend services to be accessible at the same origin.  If you're running services on different hosts/ports, set the `REACT_APP_API_GATEWAY` environment variable before building the application.