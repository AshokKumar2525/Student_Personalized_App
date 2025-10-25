"""
Pre-built roadmap templates for common domains
Used as fallback when AI generation fails
"""

def get_domain_template(domain: str, level: str) -> dict:
    """Get template roadmap for a specific domain and level"""
    
    templates = {
        'web': get_web_dev_template,
        'flutter': get_flutter_template,
        'python': get_python_template,
        'ai-ml': get_ai_ml_template,
        'data-science': get_data_science_template,
    }
    
    template_func = templates.get(domain, get_generic_template)
    return template_func(level)


def get_web_dev_template(level: str) -> dict:
    """Web Development template"""
    
    return {
        "domain": "web",
        "level": level,
        "estimated_completion": "16 weeks",
        "courses": [
            {
                "title": "HTML & CSS Fundamentals",
                "description": "Master the building blocks of web development",
                "order": 1,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "HTML5 Semantic Structure",
                        "description": "Learn modern HTML elements and document structure",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["HTML tags", "Semantic elements", "Forms"],
                        "resources": [
                            {"title": "HTML Basics", "type": "video", "difficulty": "beginner"}
                        ]
                    },
                    {
                        "title": "CSS Fundamentals & Selectors",
                        "description": "Style your web pages with CSS",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["CSS selectors", "Box model", "Colors"],
                        "resources": [
                            {"title": "CSS Styling Guide", "type": "video", "difficulty": "beginner"}
                        ]
                    },
                    {
                        "title": "Flexbox & Grid Layouts",
                        "description": "Modern CSS layout techniques",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Flexbox", "CSS Grid", "Responsive design"],
                        "resources": [
                            {"title": "Flexbox Tutorial", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Responsive Web Design",
                        "description": "Create mobile-friendly websites",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["Media queries", "Mobile-first", "Viewport"],
                        "resources": [
                            {"title": "Responsive Design Patterns", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "CSS Animations & Transitions",
                        "description": "Add motion to your designs",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Transitions", "Animations", "Keyframes"],
                        "resources": [
                            {"title": "CSS Animations", "type": "video", "difficulty": "intermediate"}
                        ]
                    }
                ]
            },
            {
                "title": "JavaScript Essentials",
                "description": "Learn programming fundamentals with JavaScript",
                "order": 2,
                "estimated_time": 900,
                "modules": [
                    {
                        "title": "JavaScript Syntax & Variables",
                        "description": "Learn JavaScript basics",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Variables", "Data types", "Operators"],
                        "resources": [
                            {"title": "JS Fundamentals", "type": "video", "difficulty": "beginner"}
                        ]
                    },
                    {
                        "title": "Functions & Scope",
                        "description": "Master JavaScript functions",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Functions", "Arrow functions", "Scope"],
                        "resources": [
                            {"title": "JavaScript Functions", "type": "video", "difficulty": "beginner"}
                        ]
                    },
                    {
                        "title": "DOM Manipulation",
                        "description": "Interact with HTML using JavaScript",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["DOM", "Events", "Element selection"],
                        "resources": [
                            {"title": "DOM Manipulation Guide", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Arrays & Objects",
                        "description": "Work with complex data structures",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["Arrays", "Objects", "Array methods"],
                        "resources": [
                            {"title": "JS Data Structures", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Async JavaScript & Promises",
                        "description": "Handle asynchronous operations",
                        "order": 5,
                        "estimated_time": 180,
                        "key_concepts": ["Promises", "Async/await", "Fetch API"],
                        "resources": [
                            {"title": "Async JavaScript", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "ES6+ Modern Features",
                        "description": "Learn modern JavaScript syntax",
                        "order": 6,
                        "estimated_time": 90,
                        "key_concepts": ["Destructuring", "Spread operator", "Modules"],
                        "resources": [
                            {"title": "Modern JavaScript", "type": "video", "difficulty": "intermediate"}
                        ]
                    }
                ]
            },
            {
                "title": "React.js Frontend Framework",
                "description": "Build dynamic user interfaces with React",
                "order": 3,
                "estimated_time": 1080,
                "modules": [
                    {
                        "title": "React Fundamentals & JSX",
                        "description": "Introduction to React",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Components", "JSX", "Props"],
                        "resources": [
                            {"title": "React Basics", "type": "video", "difficulty": "beginner"}
                        ]
                    },
                    {
                        "title": "State Management with Hooks",
                        "description": "Manage component state",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["useState", "useEffect", "Custom hooks"],
                        "resources": [
                            {"title": "React Hooks Deep Dive", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "React Router & Navigation",
                        "description": "Build multi-page applications",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Routing", "Navigation", "URL parameters"],
                        "resources": [
                            {"title": "React Router Tutorial", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Forms & User Input",
                        "description": "Handle user interactions",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["Forms", "Validation", "Controlled components"],
                        "resources": [
                            {"title": "React Forms Guide", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "API Integration & Data Fetching",
                        "description": "Connect to backend services",
                        "order": 5,
                        "estimated_time": 180,
                        "key_concepts": ["REST APIs", "Axios", "Error handling"],
                        "resources": [
                            {"title": "React API Integration", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "React Performance Optimization",
                        "description": "Optimize React applications",
                        "order": 6,
                        "estimated_time": 120,
                        "key_concepts": ["Memoization", "Code splitting", "Lazy loading"],
                        "resources": [
                            {"title": "React Performance", "type": "video", "difficulty": "advanced"}
                        ]
                    },
                    {
                        "title": "Building a Complete React Project",
                        "description": "Apply all learned concepts",
                        "order": 7,
                        "estimated_time": 240,
                        "key_concepts": ["Project structure", "Best practices", "Deployment"],
                        "resources": [
                            {"title": "React Project Tutorial", "type": "video", "difficulty": "intermediate"}
                        ]
                    }
                ]
            },
            {
                "title": "Backend Development with Node.js",
                "description": "Build server-side applications",
                "order": 4,
                "estimated_time": 900,
                "modules": [
                    {
                        "title": "Node.js & Express Fundamentals",
                        "description": "Introduction to backend development",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Node.js", "Express", "Middleware"],
                        "resources": [
                            {"title": "Node.js Basics", "type": "video", "difficulty": "beginner"}
                        ]
                    },
                    {
                        "title": "RESTful API Design",
                        "description": "Create professional APIs",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["REST principles", "HTTP methods", "Status codes"],
                        "resources": [
                            {"title": "REST API Tutorial", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Database Integration (MongoDB)",
                        "description": "Store and retrieve data",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["MongoDB", "Mongoose", "CRUD operations"],
                        "resources": [
                            {"title": "MongoDB with Node", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Authentication & Authorization",
                        "description": "Secure your applications",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["JWT", "Bcrypt", "Auth middleware"],
                        "resources": [
                            {"title": "Node.js Authentication", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Error Handling & Validation",
                        "description": "Build robust backends",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Error handling", "Input validation", "Logging"],
                        "resources": [
                            {"title": "Error Handling Best Practices", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "API Testing & Documentation",
                        "description": "Test and document your APIs",
                        "order": 6,
                        "estimated_time": 90,
                        "key_concepts": ["Jest", "Supertest", "API documentation"],
                        "resources": [
                            {"title": "API Testing Guide", "type": "video", "difficulty": "intermediate"}
                        ]
                    }
                ]
            },
            {
                "title": "Full-Stack Project Development",
                "description": "Build complete web applications",
                "order": 5,
                "estimated_time": 1200,
                "modules": [
                    {
                        "title": "Project Planning & Architecture",
                        "description": "Design your application",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["System design", "Database schema", "API design"],
                        "resources": [
                            {"title": "Full-Stack Architecture", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Frontend Development",
                        "description": "Build the user interface",
                        "order": 2,
                        "estimated_time": 300,
                        "key_concepts": ["Component structure", "State management", "Styling"],
                        "resources": [
                            {"title": "Frontend Best Practices", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Backend API Implementation",
                        "description": "Create backend services",
                        "order": 3,
                        "estimated_time": 300,
                        "key_concepts": ["API endpoints", "Database operations", "Authentication"],
                        "resources": [
                            {"title": "Backend Implementation", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Frontend-Backend Integration",
                        "description": "Connect your application",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["API calls", "Error handling", "Loading states"],
                        "resources": [
                            {"title": "Full-Stack Integration", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Testing & Quality Assurance",
                        "description": "Ensure code quality",
                        "order": 5,
                        "estimated_time": 150,
                        "key_concepts": ["Unit tests", "Integration tests", "E2E tests"],
                        "resources": [
                            {"title": "Testing Full-Stack Apps", "type": "video", "difficulty": "advanced"}
                        ]
                    },
                    {
                        "title": "Deployment & DevOps",
                        "description": "Deploy to production",
                        "order": 6,
                        "estimated_time": 150,
                        "key_concepts": ["Deployment", "CI/CD", "Monitoring"],
                        "resources": [
                            {"title": "Web App Deployment", "type": "video", "difficulty": "advanced"}
                        ]
                    }
                ]
            },
            {
                "title": "Advanced Topics & Best Practices",
                "description": "Become a professional developer",
                "order": 6,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "TypeScript for JavaScript",
                        "description": "Add type safety to your code",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Types", "Interfaces", "Generics"],
                        "resources": [
                            {"title": "TypeScript Essentials", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Advanced State Management",
                        "description": "Handle complex application state",
                        "order": 2,
                        "estimated_time": 120,
                        "key_concepts": ["Context API", "Redux", "State patterns"],
                        "resources": [
                            {"title": "State Management Patterns", "type": "video", "difficulty": "advanced"}
                        ]
                    },
                    {
                        "title": "Web Security Best Practices",
                        "description": "Secure your applications",
                        "order": 3,
                        "estimated_time": 120,
                        "key_concepts": ["XSS", "CSRF", "Security headers"],
                        "resources": [
                            {"title": "Web Security Guide", "type": "video", "difficulty": "advanced"}
                        ]
                    },
                    {
                        "title": "Performance Optimization",
                        "description": "Build fast applications",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Caching", "CDN", "Lazy loading"],
                        "resources": [
                            {"title": "Web Performance", "type": "video", "difficulty": "advanced"}
                        ]
                    },
                    {
                        "title": "Code Quality & Maintenance",
                        "description": "Write maintainable code",
                        "order": 5,
                        "estimated_time": 90,
                        "key_concepts": ["Clean code", "Refactoring", "Documentation"],
                        "resources": [
                            {"title": "Code Quality Best Practices", "type": "video", "difficulty": "intermediate"}
                        ]
                    },
                    {
                        "title": "Career Development & Portfolio",
                        "description": "Prepare for the job market",
                        "order": 6,
                        "estimated_time": 120,
                        "key_concepts": ["Portfolio", "GitHub profile", "Interview prep"],
                        "resources": [
                            {"title": "Developer Career Guide", "type": "video", "difficulty": "beginner"}
                        ]
                    }
                ]
            }
        ]
    }


def get_flutter_template(level: str) -> dict:
    """Flutter Development template"""
    return {
        "domain": "flutter",
        "level": level,
        "estimated_completion": "14 weeks",
        "courses": [
            {
                "title": "Dart Programming Language",
                "description": "Master Dart fundamentals",
                "order": 1,
                "estimated_time": 600,
                "modules": [
                    {
                        "title": "Dart Basics & Syntax",
                        "description": "Learn Dart programming",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Variables", "Functions", "Control flow"],
                        "resources": [{"title": "Dart Fundamentals", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Object-Oriented Programming",
                        "description": "OOP in Dart",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["Classes", "Inheritance", "Mixins"],
                        "resources": [{"title": "Dart OOP", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Async Programming",
                        "description": "Handle asynchronous operations",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Future", "Async/await", "Streams"],
                        "resources": [{"title": "Dart Async", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Collections & Generics",
                        "description": "Work with data structures",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["Lists", "Maps", "Sets", "Generics"],
                        "resources": [{"title": "Dart Collections", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Flutter UI Development",
                "description": "Build beautiful user interfaces",
                "order": 2,
                "estimated_time": 840,
                "modules": [
                    {
                        "title": "Flutter Basics & Widgets",
                        "description": "Introduction to Flutter",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Widgets", "StatelessWidget", "StatefulWidget"],
                        "resources": [{"title": "Flutter Basics", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Layout & Design",
                        "description": "Create responsive layouts",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["Row", "Column", "Container", "Flex"],
                        "resources": [{"title": "Flutter Layouts", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Navigation & Routing",
                        "description": "Multi-screen applications",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Navigator", "Routes", "Named routes"],
                        "resources": [{"title": "Flutter Navigation", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "State Management",
                        "description": "Manage app state effectively",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["Provider", "setState", "State patterns"],
                        "resources": [{"title": "Flutter State Management", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Forms & Validation",
                        "description": "Handle user input",
                        "order": 5,
                        "estimated_time": 180,
                        "key_concepts": ["Forms", "Validation", "TextFormField"],
                        "resources": [{"title": "Flutter Forms", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            # Additional courses follow same pattern...
            {
                "title": "Advanced Flutter Features",
                "description": "Master advanced Flutter concepts",
                "order": 3,
                "estimated_time": 900,
                "modules": [
                    {
                        "title": "Animations & Transitions",
                        "description": "Create smooth animations",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["AnimationController", "Tween", "Hero animations"],
                        "resources": [{"title": "Flutter Animations", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "API Integration",
                        "description": "Connect to backend services",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["HTTP", "JSON", "Error handling"],
                        "resources": [{"title": "Flutter API", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Local Storage",
                        "description": "Store data locally",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["SharedPreferences", "SQLite", "Hive"],
                        "resources": [{"title": "Flutter Storage", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Firebase Integration",
                        "description": "Use Firebase services",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["Authentication", "Firestore", "Cloud functions"],
                        "resources": [{"title": "Flutter Firebase", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Testing & Debugging",
                        "description": "Ensure app quality",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Unit tests", "Widget tests", "Debugging"],
                        "resources": [{"title": "Flutter Testing", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "App Deployment",
                        "description": "Publish to app stores",
                        "order": 6,
                        "estimated_time": 120,
                        "key_concepts": ["App signing", "Play Store", "App Store"],
                        "resources": [{"title": "Flutter Deployment", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            # Add 3 more courses to reach 6 total
            {
                "title": "Flutter Project Development",
                "description": "Build complete applications",
                "order": 4,
                "estimated_time": 960,
                "modules": [
                    {
                        "title": "Project Architecture",
                        "description": "Design app structure",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Clean architecture", "Folder structure", "Dependencies"],
                        "resources": [{"title": "Flutter Architecture", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Building E-commerce App",
                        "description": "Create shopping application",
                        "order": 2,
                        "estimated_time": 240,
                        "key_concepts": ["Product catalog", "Cart", "Checkout"],
                        "resources": [{"title": "Flutter E-commerce", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Social Media Features",
                        "description": "Add social functionality",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Posts", "Comments", "Likes"],
                        "resources": [{"title": "Flutter Social Features", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Real-time Features",
                        "description": "Implement live updates",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["WebSocket", "Streams", "Push notifications"],
                        "resources": [{"title": "Flutter Real-time", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Performance Optimization",
                        "description": "Optimize app performance",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Performance profiling", "Memory management", "Build optimization"],
                        "resources": [{"title": "Flutter Performance", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Production Deployment",
                        "description": "Launch your app",
                        "order": 6,
                        "estimated_time": 120,
                        "key_concepts": ["Release builds", "App store submission", "Analytics"],
                        "resources": [{"title": "Flutter Production", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Platform-Specific Development",
                "description": "Native platform integration",
                "order": 5,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "Platform Channels",
                        "description": "Communicate with native code",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Method channels", "Event channels", "Native integration"],
                        "resources": [{"title": "Flutter Platform Channels", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Camera & Media",
                        "description": "Access device features",
                        "order": 2,
                        "estimated_time": 120,
                        "key_concepts": ["Camera", "Image picker", "Video player"],
                        "resources": [{"title": "Flutter Media", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Location & Maps",
                        "description": "Integrate location services",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["GPS", "Google Maps", "Geolocation"],
                        "resources": [{"title": "Flutter Location", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Permissions & Security",
                        "description": "Handle app permissions",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Runtime permissions", "Security", "Biometrics"],
                        "resources": [{"title": "Flutter Security", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Background Processing",
                        "description": "Run tasks in background",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Background tasks", "Isolates", "Work manager"],
                        "resources": [{"title": "Flutter Background", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "In-App Purchases",
                        "description": "Monetize your app",
                        "order": 6,
                        "estimated_time": 60,
                        "key_concepts": ["IAP", "Subscriptions", "Payment processing"],
                        "resources": [{"title": "Flutter IAP", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Professional Flutter Development",
                "description": "Industry best practices",
                "order": 6,
                "estimated_time": 600,
                "modules": [
                    {
                        "title": "Code Quality & Standards",
                        "description": "Write professional code",
                        "order": 1,
                        "estimated_time": 90,
                        "key_concepts": ["Linting", "Code style", "Documentation"],
                        "resources": [{"title": "Flutter Best Practices", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "CI/CD for Flutter",
                        "description": "Automate your workflow",
                        "order": 2,
                        "estimated_time": 120,
                        "key_concepts": ["GitHub Actions", "Fastlane", "Automated testing"],
                        "resources": [{"title": "Flutter CI/CD", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "App Analytics",
                        "description": "Track user behavior",
                        "order": 3,
                        "estimated_time": 90,
                        "key_concepts": ["Firebase Analytics", "Crashlytics", "User tracking"],
                        "resources": [{"title": "Flutter Analytics", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Accessibility",
                        "description": "Make apps accessible",
                        "order": 4,
                        "estimated_time": 90,
                        "key_concepts": ["Screen readers", "Semantic labels", "WCAG"],
                        "resources": [{"title": "Flutter Accessibility", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Internationalization",
                        "description": "Support multiple languages",
                        "order": 5,
                        "estimated_time": 90,
                        "key_concepts": ["i18n", "Localization", "RTL support"],
                        "resources": [{"title": "Flutter i18n", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Portfolio & Career",
                        "description": "Build your career",
                        "order": 6,
                        "estimated_time": 120,
                        "key_concepts": ["Portfolio apps", "Open source", "Job preparation"],
                        "resources": [{"title": "Flutter Career Guide", "type": "video", "difficulty": "beginner"}]
                    }
                ]
            }
        ]
    }


def get_python_template(level: str) -> dict:
    """Python Programming template"""
    return {
        "domain": "python",
        "level": level,
        "estimated_completion": "12 weeks",
        "courses": [
            {
                "title": "Python Fundamentals",
                "description": "Learn Python basics",
                "order": 1,
                "estimated_time": 600,
                "modules": [
                    {
                        "title": "Python Syntax & Variables",
                        "description": "Get started with Python",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Variables", "Data types", "Operators"],
                        "resources": [{"title": "Python Basics", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Control Flow",
                        "description": "Conditional statements and loops",
                        "order": 2,
                        "estimated_time": 120,
                        "key_concepts": ["If statements", "For loops", "While loops"],
                        "resources": [{"title": "Python Control Flow", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Functions",
                        "description": "Write reusable code",
                        "order": 3,
                        "estimated_time": 120,
                        "key_concepts": ["Functions", "Parameters", "Return values"],
                        "resources": [{"title": "Python Functions", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Data Structures",
                        "description": "Lists, tuples, sets, and dictionaries",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Lists", "Dictionaries", "Sets", "Tuples"],
                        "resources": [{"title": "Python Data Structures", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "File Handling",
                        "description": "Read and write files",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["File I/O", "CSV", "JSON"],
                        "resources": [{"title": "Python File Handling", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            # Add 5 more courses following the same pattern
            {
                "title": "Object-Oriented Programming",
                "description": "Master OOP in Python",
                "order": 2,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "Classes & Objects",
                        "description": "Introduction to OOP",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Classes", "Objects", "Methods"],
                        "resources": [{"title": "Python OOP Basics", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Inheritance & Polymorphism",
                        "description": "Advanced OOP concepts",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Inheritance", "Polymorphism", "Super"],
                        "resources": [{"title": "Python Inheritance", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Encapsulation & Abstraction",
                        "description": "OOP principles",
                        "order": 3,
                        "estimated_time": 120,
                        "key_concepts": ["Private attributes", "Getters/setters", "Abstract classes"],
                        "resources": [{"title": "Python Encapsulation", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Magic Methods",
                        "description": "Special methods in Python",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["__init__", "__str__", "__add__"],
                        "resources": [{"title": "Python Magic Methods", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Design Patterns",
                        "description": "Common OOP patterns",
                        "order": 5,
                        "estimated_time": 180,
                        "key_concepts": ["Singleton", "Factory", "Observer"],
                        "resources": [{"title": "Python Design Patterns", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Python Libraries & Frameworks",
                "description": "Work with popular Python libraries",
                "order": 3,
                "estimated_time": 840,
                "modules": [
                    {
                        "title": "NumPy for Numerical Computing",
                        "description": "Array operations and math",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Arrays", "Mathematical operations", "Broadcasting"],
                        "resources": [{"title": "NumPy Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Pandas for Data Analysis",
                        "description": "Work with dataframes",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["DataFrames", "Data manipulation", "Analysis"],
                        "resources": [{"title": "Pandas Basics", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Matplotlib & Visualization",
                        "description": "Create data visualizations",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Plotting", "Charts", "Graphs"],
                        "resources": [{"title": "Python Visualization", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Requests & Web Scraping",
                        "description": "Interact with APIs and web",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["HTTP requests", "BeautifulSoup", "APIs"],
                        "resources": [{"title": "Python Web Scraping", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Flask Web Development",
                        "description": "Build web applications",
                        "order": 5,
                        "estimated_time": 210,
                        "key_concepts": ["Routes", "Templates", "Forms"],
                        "resources": [{"title": "Flask Tutorial", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Advanced Python Concepts",
                "description": "Master advanced topics",
                "order": 4,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "Decorators & Generators",
                        "description": "Advanced Python features",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Decorators", "Generators", "Yield"],
                        "resources": [{"title": "Python Decorators", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Context Managers",
                        "description": "Resource management",
                        "order": 2,
                        "estimated_time": 90,
                        "key_concepts": ["with statement", "__enter__", "__exit__"],
                        "resources": [{"title": "Python Context Managers", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Multithreading & Multiprocessing",
                        "description": "Concurrent programming",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Threading", "Multiprocessing", "Async IO"],
                        "resources": [{"title": "Python Concurrency", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Error Handling & Debugging",
                        "description": "Handle errors effectively",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Exceptions", "Try/except", "Debugging tools"],
                        "resources": [{"title": "Python Error Handling", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Testing & Quality Assurance",
                        "description": "Write tests for your code",
                        "order": 5,
                        "estimated_time": 180,
                        "key_concepts": ["Unittest", "Pytest", "TDD"],
                        "resources": [{"title": "Python Testing", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Database & Backend Development",
                "description": "Work with databases",
                "order": 5,
                "estimated_time": 780,
                "modules": [
                    {
                        "title": "SQL Fundamentals",
                        "description": "Learn database basics",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["SQL queries", "Joins", "Aggregations"],
                        "resources": [{"title": "SQL with Python", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "SQLite & Python",
                        "description": "Work with SQLite databases",
                        "order": 2,
                        "estimated_time": 120,
                        "key_concepts": ["SQLite3 module", "CRUD operations", "Transactions"],
                        "resources": [{"title": "Python SQLite", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "SQLAlchemy ORM",
                        "description": "Object-relational mapping",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Models", "Sessions", "Relationships"],
                        "resources": [{"title": "SQLAlchemy Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "RESTful API Development",
                        "description": "Build APIs with Flask",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["REST principles", "API endpoints", "JSON"],
                        "resources": [{"title": "Flask REST API", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Authentication & Security",
                        "description": "Secure your applications",
                        "order": 5,
                        "estimated_time": 150,
                        "key_concepts": ["JWT", "Password hashing", "Authorization"],
                        "resources": [{"title": "Python Security", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Python Projects & Career",
                "description": "Build portfolio and prepare for career",
                "order": 6,
                "estimated_time": 960,
                "modules": [
                    {
                        "title": "Project Planning",
                        "description": "Plan your Python project",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Requirements", "Architecture", "Tools"],
                        "resources": [{"title": "Python Project Planning", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Building a Web Application",
                        "description": "Complete Flask project",
                        "order": 2,
                        "estimated_time": 300,
                        "key_concepts": ["Full-stack development", "Database integration", "Deployment"],
                        "resources": [{"title": "Flask Project Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Data Analysis Project",
                        "description": "Analyze real-world data",
                        "order": 3,
                        "estimated_time": 240,
                        "key_concepts": ["Data cleaning", "Analysis", "Visualization"],
                        "resources": [{"title": "Python Data Project", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Automation Scripts",
                        "description": "Automate tasks with Python",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["File automation", "Web automation", "Task scheduling"],
                        "resources": [{"title": "Python Automation", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Deployment & DevOps",
                        "description": "Deploy Python applications",
                        "order": 5,
                        "estimated_time": 90,
                        "key_concepts": ["Heroku", "Docker", "CI/CD"],
                        "resources": [{"title": "Python Deployment", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Career Preparation",
                        "description": "Prepare for Python jobs",
                        "order": 6,
                        "estimated_time": 90,
                        "key_concepts": ["Portfolio", "GitHub", "Interview prep"],
                        "resources": [{"title": "Python Career Guide", "type": "video", "difficulty": "beginner"}]
                    }
                ]
            }
        ]
    }


def get_ai_ml_template(level: str) -> dict:
    """AI & Machine Learning template"""
    return {
        "domain": "ai-ml",
        "level": level,
        "estimated_completion": "18 weeks",
        "courses": [
            {
                "title": "Python for Data Science",
                "description": "Essential Python for ML",
                "order": 1,
                "estimated_time": 600,
                "modules": [
                    {
                        "title": "NumPy Fundamentals",
                        "description": "Array operations for ML",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Arrays", "Broadcasting", "Linear algebra"],
                        "resources": [{"title": "NumPy for ML", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Pandas Data Manipulation",
                        "description": "Data preprocessing",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["DataFrames", "Data cleaning", "Feature engineering"],
                        "resources": [{"title": "Pandas for ML", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Data Visualization",
                        "description": "Visualize ML data",
                        "order": 3,
                        "estimated_time": 120,
                        "key_concepts": ["Matplotlib", "Seaborn", "Plotly"],
                        "resources": [{"title": "ML Visualization", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Statistics for ML",
                        "description": "Statistical foundations",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Probability", "Distributions", "Hypothesis testing"],
                        "resources": [{"title": "Statistics for ML", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Linear Algebra Basics",
                        "description": "Math for ML",
                        "order": 5,
                        "estimated_time": 90,
                        "key_concepts": ["Vectors", "Matrices", "Eigenvalues"],
                        "resources": [{"title": "Linear Algebra ML", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Machine Learning Fundamentals",
                "description": "Core ML concepts",
                "order": 2,
                "estimated_time": 900,
                "modules": [
                    {
                        "title": "Introduction to ML",
                        "description": "ML basics and types",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Supervised learning", "Unsupervised learning", "ML workflow"],
                        "resources": [{"title": "ML Introduction", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Linear Regression",
                        "description": "Your first ML algorithm",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Regression", "Cost function", "Gradient descent"],
                        "resources": [{"title": "Linear Regression Tutorial", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Logistic Regression",
                        "description": "Classification basics",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Binary classification", "Sigmoid function", "Decision boundary"],
                        "resources": [{"title": "Logistic Regression", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Decision Trees & Random Forests",
                        "description": "Tree-based models",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["Decision trees", "Random forests", "Feature importance"],
                        "resources": [{"title": "Tree-based Models", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Support Vector Machines",
                        "description": "Advanced classification",
                        "order": 5,
                        "estimated_time": 150,
                        "key_concepts": ["SVM", "Kernels", "Margin optimization"],
                        "resources": [{"title": "SVM Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Model Evaluation",
                        "description": "Assess model performance",
                        "order": 6,
                        "estimated_time": 150,
                        "key_concepts": ["Cross-validation", "Metrics", "Overfitting"],
                        "resources": [{"title": "ML Model Evaluation", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Deep Learning with TensorFlow",
                "description": "Neural networks and deep learning",
                "order": 3,
                "estimated_time": 1080,
                "modules": [
                    {
                        "title": "Neural Networks Basics",
                        "description": "Introduction to neural networks",
                        "order": 1,
                        "estimated_time": 180,
                        "key_concepts": ["Perceptron", "Activation functions", "Backpropagation"],
                        "resources": [{"title": "Neural Networks 101", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "TensorFlow & Keras",
                        "description": "Deep learning frameworks",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["TensorFlow basics", "Keras API", "Model building"],
                        "resources": [{"title": "TensorFlow Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Convolutional Neural Networks",
                        "description": "CNNs for image processing",
                        "order": 3,
                        "estimated_time": 210,
                        "key_concepts": ["Convolution", "Pooling", "Image classification"],
                        "resources": [{"title": "CNN Deep Dive", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Recurrent Neural Networks",
                        "description": "RNNs for sequential data",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["RNN", "LSTM", "GRU"],
                        "resources": [{"title": "RNN Tutorial", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Transfer Learning",
                        "description": "Use pre-trained models",
                        "order": 5,
                        "estimated_time": 150,
                        "key_concepts": ["Pre-trained models", "Fine-tuning", "Feature extraction"],
                        "resources": [{"title": "Transfer Learning", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Model Optimization",
                        "description": "Improve model performance",
                        "order": 6,
                        "estimated_time": 180,
                        "key_concepts": ["Hyperparameter tuning", "Regularization", "Batch normalization"],
                        "resources": [{"title": "Model Optimization", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Natural Language Processing",
                "description": "NLP and text processing",
                "order": 4,
                "estimated_time": 840,
                "modules": [
                    {
                        "title": "Text Preprocessing",
                        "description": "Prepare text data",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Tokenization", "Stemming", "Lemmatization"],
                        "resources": [{"title": "NLP Preprocessing", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Word Embeddings",
                        "description": "Represent words as vectors",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Word2Vec", "GloVe", "Embeddings"],
                        "resources": [{"title": "Word Embeddings", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Sentiment Analysis",
                        "description": "Analyze text sentiment",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Classification", "Sentiment models", "Feature extraction"],
                        "resources": [{"title": "Sentiment Analysis", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Transformers & BERT",
                        "description": "Modern NLP models",
                        "order": 4,
                        "estimated_time": 210,
                        "key_concepts": ["Attention", "BERT", "Transformers"],
                        "resources": [{"title": "Transformers Tutorial", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Text Generation",
                        "description": "Generate text with AI",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["GPT", "Text generation", "Language models"],
                        "resources": [{"title": "Text Generation", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "NLP Project",
                        "description": "Build NLP application",
                        "order": 6,
                        "estimated_time": 90,
                        "key_concepts": ["End-to-end NLP", "Deployment", "API"],
                        "resources": [{"title": "NLP Project", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Computer Vision",
                "description": "Image and video processing",
                "order": 5,
                "estimated_time": 840,
                "modules": [
                    {
                        "title": "Image Processing Basics",
                        "description": "Fundamentals of computer vision",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["OpenCV", "Image operations", "Filters"],
                        "resources": [{"title": "Computer Vision Basics", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Image Classification",
                        "description": "Classify images with CNNs",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["CNNs", "Image classification", "Data augmentation"],
                        "resources": [{"title": "Image Classification", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Object Detection",
                        "description": "Detect objects in images",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["YOLO", "R-CNN", "Bounding boxes"],
                        "resources": [{"title": "Object Detection", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Image Segmentation",
                        "description": "Pixel-level classification",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["Semantic segmentation", "Instance segmentation", "U-Net"],
                        "resources": [{"title": "Image Segmentation", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Face Recognition",
                        "description": "Facial detection and recognition",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Face detection", "Face recognition", "Facial landmarks"],
                        "resources": [{"title": "Face Recognition", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Video Analysis",
                        "description": "Process video streams",
                        "order": 6,
                        "estimated_time": 90,
                        "key_concepts": ["Video processing", "Motion detection", "Tracking"],
                        "resources": [{"title": "Video Analysis", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "ML Deployment & Production",
                "description": "Deploy ML models to production",
                "order": 6,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "Model Serialization",
                        "description": "Save and load models",
                        "order": 1,
                        "estimated_time": 90,
                        "key_concepts": ["Pickle", "SavedModel", "ONNX"],
                        "resources": [{"title": "Model Serialization", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Flask API for ML",
                        "description": "Build ML APIs",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["REST API", "Flask", "Model serving"],
                        "resources": [{"title": "ML API Development", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Docker for ML",
                        "description": "Containerize ML applications",
                        "order": 3,
                        "estimated_time": 120,
                        "key_concepts": ["Docker", "Containers", "Images"],
                        "resources": [{"title": "Docker for ML", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Cloud Deployment",
                        "description": "Deploy to cloud platforms",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["AWS", "GCP", "Azure ML"],
                        "resources": [{"title": "ML Cloud Deployment", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "ML Monitoring",
                        "description": "Monitor model performance",
                        "order": 5,
                        "estimated_time": 90,
                        "key_concepts": ["Model drift", "Monitoring", "Logging"],
                        "resources": [{"title": "ML Monitoring", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "MLOps & Career",
                        "description": "ML engineering best practices",
                        "order": 6,
                        "estimated_time": 90,
                        "key_concepts": ["MLOps", "CI/CD", "Portfolio"],
                        "resources": [{"title": "MLOps Guide", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            }
        ]
    }


def get_data_science_template(level: str) -> dict:
    """Data Science template - simplified version"""
    return {
        "domain": "data-science",
        "level": level,
        "estimated_completion": "16 weeks",
        "courses": [
            {
                "title": "Data Science Foundations",
                "description": "Essential data science skills",
                "order": 1,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "Python for Data Science",
                        "description": "Python programming basics",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Python basics", "Data types", "Control flow"],
                        "resources": [{"title": "Python DS Intro", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "NumPy & Pandas",
                        "description": "Data manipulation libraries",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["NumPy arrays", "Pandas DataFrames", "Data cleaning"],
                        "resources": [{"title": "NumPy Pandas Tutorial", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Data Visualization",
                        "description": "Visualize data effectively",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Matplotlib", "Seaborn", "Plotly"],
                        "resources": [{"title": "Data Visualization", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Statistics Fundamentals",
                        "description": "Statistical analysis basics",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Descriptive stats", "Probability", "Distributions"],
                        "resources": [{"title": "Statistics for DS", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "SQL for Data Science",
                        "description": "Query databases effectively",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["SQL queries", "Joins", "Aggregations"],
                        "resources": [{"title": "SQL Tutorial", "type": "video", "difficulty": "beginner"}]
                    }
                ]
            },
            # Add 5 more courses...
            {
                "title": "Exploratory Data Analysis",
                "description": "Analyze and understand data",
                "order": 2,
                "estimated_time": 600,
                "modules": [
                    {
                        "title": "Data Collection",
                        "description": "Gather data from sources",
                        "order": 1,
                        "estimated_time": 90,
                        "key_concepts": ["APIs", "Web scraping", "Databases"],
                        "resources": [{"title": "Data Collection", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Data Cleaning",
                        "description": "Prepare data for analysis",
                        "order": 2,
                        "estimated_time": 120,
                        "key_concepts": ["Missing data", "Outliers", "Data transformation"],
                        "resources": [{"title": "Data Cleaning", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Exploratory Analysis",
                        "description": "Discover patterns in data",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["EDA techniques", "Statistical summaries", "Visualization"],
                        "resources": [{"title": "EDA Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Feature Engineering",
                        "description": "Create meaningful features",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Feature creation", "Encoding", "Scaling"],
                        "resources": [{"title": "Feature Engineering", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Data Storytelling",
                        "description": "Communicate insights",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Visualization", "Reporting", "Presentation"],
                        "resources": [{"title": "Data Storytelling", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Machine Learning for DS",
                "description": "Apply ML to data problems",
                "order": 3,
                "estimated_time": 900,
                "modules": [
                    {
                        "title": "ML Fundamentals",
                        "description": "Introduction to machine learning",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Supervised learning", "Unsupervised learning", "Model training"],
                        "resources": [{"title": "ML Basics", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Regression Models",
                        "description": "Predict continuous values",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Linear regression", "Polynomial regression", "Metrics"],
                        "resources": [{"title": "Regression Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Classification Models",
                        "description": "Predict categories",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Logistic regression", "Decision trees", "Random forests"],
                        "resources": [{"title": "Classification Models", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Clustering",
                        "description": "Group similar data points",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["K-means", "Hierarchical clustering", "DBSCAN"],
                        "resources": [{"title": "Clustering Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Model Evaluation",
                        "description": "Assess model performance",
                        "order": 5,
                        "estimated_time": 150,
                        "key_concepts": ["Cross-validation", "Metrics", "Model selection"],
                        "resources": [{"title": "Model Evaluation", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Ensemble Methods",
                        "description": "Combine multiple models",
                        "order": 6,
                        "estimated_time": 120,
                        "key_concepts": ["Bagging", "Boosting", "Stacking"],
                        "resources": [{"title": "Ensemble Methods", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Advanced Analytics",
                "description": "Advanced data science techniques",
                "order": 4,
                "estimated_time": 780,
                "modules": [
                    {
                        "title": "Time Series Analysis",
                        "description": "Analyze temporal data",
                        "order": 1,
                        "estimated_time": 180,
                        "key_concepts": ["Time series", "ARIMA", "Forecasting"],
                        "resources": [{"title": "Time Series Tutorial", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "A/B Testing",
                        "description": "Design and analyze experiments",
                        "order": 2,
                        "estimated_time": 120,
                        "key_concepts": ["Hypothesis testing", "Statistical significance", "Experimentation"],
                        "resources": [{"title": "A/B Testing Guide", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Natural Language Processing",
                        "description": "Process text data",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Text preprocessing", "Sentiment analysis", "Topic modeling"],
                        "resources": [{"title": "NLP for DS", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Recommendation Systems",
                        "description": "Build recommender engines",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["Collaborative filtering", "Content-based", "Matrix factorization"],
                        "resources": [{"title": "Recommendation Systems", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Deep Learning Basics",
                        "description": "Introduction to neural networks",
                        "order": 5,
                        "estimated_time": 150,
                        "key_concepts": ["Neural networks", "TensorFlow", "Keras"],
                        "resources": [{"title": "Deep Learning Intro", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Big Data & Tools",
                "description": "Work with large datasets",
                "order": 5,
                "estimated_time": 660,
                "modules": [
                    {
                        "title": "Big Data Fundamentals",
                        "description": "Introduction to big data",
                        "order": 1,
                        "estimated_time": 90,
                        "key_concepts": ["Big data concepts", "Distributed computing", "Hadoop"],
                        "resources": [{"title": "Big Data Intro", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Apache Spark",
                        "description": "Process large datasets",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["Spark", "RDD", "DataFrames"],
                        "resources": [{"title": "Spark Tutorial", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Cloud Computing",
                        "description": "Work with cloud platforms",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["AWS", "GCP", "Azure"],
                        "resources": [{"title": "Cloud for DS", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Data Warehousing",
                        "description": "Store and query large data",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Data warehouse", "ETL", "BigQuery"],
                        "resources": [{"title": "Data Warehousing", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Data Engineering Basics",
                        "description": "Build data pipelines",
                        "order": 5,
                        "estimated_time": 120,
                        "key_concepts": ["Data pipelines", "Airflow", "ETL processes"],
                        "resources": [{"title": "Data Engineering", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "DS Projects & Career",
                "description": "Build portfolio and career skills",
                "order": 6,
                "estimated_time": 900,
                "modules": [
                    {
                        "title": "End-to-End DS Project",
                        "description": "Complete data science workflow",
                        "order": 1,
                        "estimated_time": 300,
                        "key_concepts": ["Project workflow", "Analysis", "Modeling"],
                        "resources": [{"title": "DS Project Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Dashboard & Reporting",
                        "description": "Create interactive dashboards",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Streamlit", "Dash", "Tableau"],
                        "resources": [{"title": "Dashboard Creation", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Model Deployment",
                        "description": "Deploy DS models",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Flask API", "Docker", "Cloud deployment"],
                        "resources": [{"title": "Model Deployment", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Kaggle Competitions",
                        "description": "Participate in competitions",
                        "order": 4,
                        "estimated_time": 120,
                        "key_concepts": ["Kaggle", "Competition strategies", "Leaderboard"],
                        "resources": [{"title": "Kaggle Guide", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Portfolio Development",
                        "description": "Build DS portfolio",
                        "order": 5,
                        "estimated_time": 90,
                        "key_concepts": ["GitHub", "Portfolio projects", "Documentation"],
                        "resources": [{"title": "DS Portfolio", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Career Preparation",
                        "description": "Prepare for DS interviews",
                        "order": 6,
                        "estimated_time": 90,
                        "key_concepts": ["Interview prep", "Resume", "Networking"],
                        "resources": [{"title": "DS Career Guide", "type": "video", "difficulty": "beginner"}]
                    }
                ]
            }
        ]
    }


def get_generic_template(level: str) -> dict:
    """Generic template for unknown domains"""
    return {
        "domain": "general",
        "level": level,
        "estimated_completion": "12 weeks",
        "courses": [
            {
                "title": "Fundamentals",
                "description": "Core concepts and basics",
                "order": 1,
                "estimated_time": 600,
                "modules": [
                    {
                        "title": "Introduction",
                        "description": "Get started with the basics",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Basic concepts", "Setup", "Environment"],
                        "resources": [{"title": "Introduction Tutorial", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Core Concepts",
                        "description": "Learn fundamental principles",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Key principles", "Best practices", "Terminology"],
                        "resources": [{"title": "Core Concepts Guide", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Practical Application",
                        "description": "Apply what you've learned",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Hands-on practice", "Real examples", "Exercises"],
                        "resources": [{"title": "Practical Tutorial", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "First Project",
                        "description": "Build your first project",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["Project setup", "Implementation", "Testing"],
                        "resources": [{"title": "Project Tutorial", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Intermediate Topics",
                "description": "Advance your skills",
                "order": 2,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "Advanced Concepts",
                        "description": "Dive deeper",
                        "order": 1,
                        "estimated_time": 180,
                        "key_concepts": ["Advanced topics", "Complex concepts", "Design patterns"],
                        "resources": [{"title": "Advanced Guide", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Best Practices",
                        "description": "Learn industry standards",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["Best practices", "Code quality", "Standards"],
                        "resources": [{"title": "Best Practices", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Tools & Frameworks",
                        "description": "Master essential tools",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Popular tools", "Frameworks", "Libraries"],
                        "resources": [{"title": "Tools Overview", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Intermediate Project",
                        "description": "Build a complex project",
                        "order": 4,
                        "estimated_time": 210,
                        "key_concepts": ["Project architecture", "Implementation", "Deployment"],
                        "resources": [{"title": "Intermediate Project", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Advanced Topics",
                "description": "Master advanced skills",
                "order": 3,
                "estimated_time": 840,
                "modules": [
                    {
                        "title": "Expert Techniques",
                        "description": "Advanced techniques",
                        "order": 1,
                        "estimated_time": 180,
                        "key_concepts": ["Expert techniques", "Optimization", "Performance"],
                        "resources": [{"title": "Expert Techniques", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Scalability",
                        "description": "Build scalable solutions",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["Scalability", "Architecture", "Systems design"],
                        "resources": [{"title": "Scalability Guide", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Security",
                        "description": "Implement security best practices",
                        "order": 3,
                        "estimated_time": 150,
                        "key_concepts": ["Security", "Authentication", "Authorization"],
                        "resources": [{"title": "Security Tutorial", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Testing",
                        "description": "Write comprehensive tests",
                        "order": 4,
                        "estimated_time": 150,
                        "key_concepts": ["Testing strategies", "TDD", "Integration tests"],
                        "resources": [{"title": "Testing Guide", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Advanced Project",
                        "description": "Build production-ready project",
                        "order": 5,
                        "estimated_time": 180,
                        "key_concepts": ["Full-stack", "Production", "Deployment"],
                        "resources": [{"title": "Advanced Project", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Specialization",
                "description": "Specialize in specific areas",
                "order": 4,
                "estimated_time": 720,
                "modules": [
                    {
                        "title": "Specialization Track 1",
                        "description": "Focus area 1",
                        "order": 1,
                        "estimated_time": 180,
                        "key_concepts": ["Specialized knowledge", "Domain expertise", "Applications"],
                        "resources": [{"title": "Specialization 1", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Specialization Track 2",
                        "description": "Focus area 2",
                        "order": 2,
                        "estimated_time": 180,
                        "key_concepts": ["Advanced applications", "Real-world use", "Case studies"],
                        "resources": [{"title": "Specialization 2", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Integration",
                        "description": "Integrate different technologies",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Integration", "APIs", "Microservices"],
                        "resources": [{"title": "Integration Guide", "type": "video", "difficulty": "advanced"}]
                    },
                    {
                        "title": "Capstone Project",
                        "description": "Complete comprehensive project",
                        "order": 4,
                        "estimated_time": 180,
                        "key_concepts": ["Full application", "All concepts", "Portfolio piece"],
                        "resources": [{"title": "Capstone Project", "type": "video", "difficulty": "advanced"}]
                    }
                ]
            },
            {
                "title": "Industry Practices",
                "description": "Learn professional workflows",
                "order": 5,
                "estimated_time": 600,
                "modules": [
                    {
                        "title": "Version Control",
                        "description": "Master Git and GitHub",
                        "order": 1,
                        "estimated_time": 120,
                        "key_concepts": ["Git", "GitHub", "Collaboration"],
                        "resources": [{"title": "Git Tutorial", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "CI/CD",
                        "description": "Continuous integration and deployment",
                        "order": 2,
                        "estimated_time": 150,
                        "key_concepts": ["CI/CD", "Automation", "DevOps"],
                        "resources": [{"title": "CI/CD Guide", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Code Review",
                        "description": "Review and improve code",
                        "order": 3,
                        "estimated_time": 90,
                        "key_concepts": ["Code review", "Quality", "Best practices"],
                        "resources": [{"title": "Code Review", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Documentation",
                        "description": "Write effective documentation",
                        "order": 4,
                        "estimated_time": 90,
                        "key_concepts": ["Documentation", "README", "API docs"],
                        "resources": [{"title": "Documentation Guide", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Team Collaboration",
                        "description": "Work effectively in teams",
                        "order": 5,
                        "estimated_time": 150,
                        "key_concepts": ["Agile", "Scrum", "Communication"],
                        "resources": [{"title": "Team Collaboration", "type": "video", "difficulty": "intermediate"}]
                    }
                ]
            },
            {
                "title": "Career Development",
                "description": "Prepare for your career",
                "order": 6,
                "estimated_time": 540,
                "modules": [
                    {
                        "title": "Portfolio Building",
                        "description": "Create an impressive portfolio",
                        "order": 1,
                        "estimated_time": 150,
                        "key_concepts": ["Portfolio", "Projects", "Presentation"],
                        "resources": [{"title": "Portfolio Guide", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Resume & LinkedIn",
                        "description": "Professional profile creation",
                        "order": 2,
                        "estimated_time": 90,
                        "key_concepts": ["Resume", "LinkedIn", "Personal brand"],
                        "resources": [{"title": "Resume Building", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Interview Preparation",
                        "description": "Ace technical interviews",
                        "order": 3,
                        "estimated_time": 180,
                        "key_concepts": ["Technical interviews", "Coding challenges", "Behavioral questions"],
                        "resources": [{"title": "Interview Prep", "type": "video", "difficulty": "intermediate"}]
                    },
                    {
                        "title": "Networking",
                        "description": "Build professional network",
                        "order": 4,
                        "estimated_time": 60,
                        "key_concepts": ["Networking", "Communities", "Mentorship"],
                        "resources": [{"title": "Networking Guide", "type": "video", "difficulty": "beginner"}]
                    },
                    {
                        "title": "Continuous Learning",
                        "description": "Keep learning and growing",
                        "order": 5,
                        "estimated_time": 60,
                        "key_concepts": ["Learning strategies", "Resources", "Growth mindset"],
                        "resources": [{"title": "Continuous Learning", "type": "video", "difficulty": "beginner"}]
                    }
                ]
            }
        ]
    }