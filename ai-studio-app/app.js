/**
 * EVENTFLOW - AI-Powered Event Platform
 * Main Application JavaScript
 */

// ============================================
// SAMPLE DATA
// ============================================

const sampleEvents = [
    {
        id: 1,
        title: "AI & Machine Learning Summit",
        date: "2026-02-07",
        time: "9:00 AM",
        location: "Convention Center",
        category: "tech",
        price: 299,
        platform: "eventbrite",
        description: "Join industry leaders for a deep dive into the latest AI and ML breakthroughs.",
        capacity: 500,
        attendees: 342
    },
    {
        id: 2,
        title: "Web3 Developers Conference",
        date: "2026-02-08",
        time: "10:00 AM",
        location: "Tech Hub",
        category: "tech",
        price: 199,
        platform: "luma",
        description: "Explore the future of decentralized applications and blockchain technology.",
        capacity: 300,
        attendees: 187
    },
    {
        id: 3,
        title: "Blockchain Expo 2026",
        date: "2026-02-10",
        time: "11:00 AM",
        location: "Crypto Center",
        category: "tech",
        price: 399,
        platform: "eventbrite",
        description: "The premier blockchain and cryptocurrency event of the year.",
        capacity: 1000,
        attendees: 756
    },
    {
        id: 4,
        title: "Startup Networking Night",
        date: "2026-02-12",
        time: "6:00 PM",
        location: "Innovation Hub",
        category: "business",
        price: 49,
        platform: "luma",
        description: "Connect with fellow entrepreneurs and investors.",
        capacity: 150,
        attendees: 98
    },
    {
        id: 5,
        title: "Electronic Music Festival",
        date: "2026-02-15",
        time: "8:00 PM",
        location: "Downtown Arena",
        category: "music",
        price: 129,
        platform: "eventbrite",
        description: "Experience world-class DJs and electronic music.",
        capacity: 5000,
        attendees: 3200
    },
    {
        id: 6,
        title: "Community Sports Day",
        date: "2026-02-20",
        time: "9:00 AM",
        location: "City Park",
        category: "sports",
        price: 0,
        platform: "luma",
        description: "Fun fitness activities for all ages.",
        capacity: 200,
        attendees: 145
    }
];

const promptTemplates = [
    {
        id: 1,
        title: "Milestone Birthday Party",
        tag: "birthday",
        description: "Themed celebration with entertainment, decorations, and personalized touches.",
        location: "Event Venue Downtown",
        time: "7:00 PM"
    },
    {
        id: 2,
        title: "Tech Conference",
        tag: "tech",
        description: "Professional conference with keynotes, panels, and networking sessions.",
        location: "Convention Center",
        time: "9:00 AM"
    },
    {
        id: 3,
        title: "Music Festival",
        tag: "music",
        description: "Multi-stage music event with live performances and food vendors.",
        location: "Outdoor Amphitheater",
        time: "3:00 PM"
    },
    {
        id: 4,
        title: "Corporate Workshop",
        tag: "business",
        description: "Team building and professional development workshop.",
        location: "Business Center",
        time: "10:00 AM"
    },
    {
        id: 5,
        title: "Charity Gala",
        tag: "social",
        description: "Elegant fundraising event with dinner and entertainment.",
        location: "Grand Ballroom",
        time: "6:00 PM"
    },
    {
        id: 6,
        title: "Sports Tournament",
        tag: "sports",
        description: "Competitive tournament with multiple categories and prizes.",
        location: "Sports Complex",
        time: "8:00 AM"
    }
];

// User data
const userData = {
    name: "Alex Morgan",
    email: "alex.morgan@email.com",
    hostedEvents: [1, 4],
    attendingEvents: [2, 3, 5],
    savedEvents: [6]
};

// ============================================
// APP STATE
// ============================================

const state = {
    currentPage: 'home',
    isListening: false,
    selectedTemplate: null,
    currentFilter: 'all'
};

// ============================================
// DOM ELEMENTS
// ============================================

const elements = {
    mainContent: document.getElementById('mainContent'),
    notificationBar: document.getElementById('notificationBar'),
    notificationToggle: document.getElementById('notificationToggle'),
    mobileMenuBtn: document.getElementById('mobileMenuBtn'),
    sideNav: document.getElementById('sideNav'),
    controlBar: document.getElementById('controlBar'),
    voiceBtn: document.getElementById('voiceBtn'),
    chatBtn: document.getElementById('chatBtn'),
    chatModal: document.getElementById('chatModal'),
    chatInput: document.getElementById('chatInput'),
    cancelChat: document.getElementById('cancelChat'),
    sendChat: document.getElementById('sendChat'),
    eventModal: document.getElementById('eventModal'),
    eventModalBody: document.getElementById('eventModalBody'),
    voiceOverlay: document.getElementById('voiceOverlay'),
    voiceTranscript: document.getElementById('voiceTranscript'),
    stopListening: document.getElementById('stopListening'),
    toastContainer: document.getElementById('toastContainer')
};

// ============================================
// PAGE TEMPLATES
// ============================================

function getHomePage() {
    return `
        <section class="hero-section">
            <div class="orb-container" id="orbContainer">
                <div class="orb" id="mainOrb">
                    <div class="orb-inner"></div>
                    <div class="orb-glow"></div>
                    <div class="orb-reflection"></div>
                </div>
                <div class="orb-pulse"></div>
            </div>
            <h1 class="hero-title">
                <span class="gradient-text">Tap the orb</span> or speak to start planning your perfect event with AI
            </h1>
            <div class="ai-response-area" id="aiResponseArea">
                <div class="response-card hidden" id="responseCard">
                    <div class="response-header">
                        <span class="response-icon">🔮</span>
                        <span class="response-title">Event Analysis</span>
                    </div>
                    <div class="response-content" id="responseContent"></div>
                </div>
                <div class="events-results hidden" id="eventsResults">
                    <div class="results-header" id="resultsHeader"></div>
                    <div class="events-list" id="eventsList"></div>
                </div>
            </div>
        </section>
    `;
}

function getDiscoverPage() {
    return `
        <div class="page-header">
            <h1>Discover Events</h1>
            <p>Find amazing experiences near you</p>
        </div>
        <div class="filters-section">
            <div class="filter-chips">
                <button class="filter-chip active" data-filter="all">All Events</button>
                <button class="filter-chip" data-filter="tech">Tech</button>
                <button class="filter-chip" data-filter="music">Music</button>
                <button class="filter-chip" data-filter="business">Business</button>
                <button class="filter-chip" data-filter="social">Social</button>
                <button class="filter-chip" data-filter="sports">Sports</button>
            </div>
            <div class="filter-row">
                <div class="filter-group">
                    <label>Date</label>
                    <input type="date" class="filter-input" id="dateFilter">
                </div>
                <div class="filter-group">
                    <label>Location</label>
                    <input type="text" class="filter-input" placeholder="City or Online" id="locationFilter">
                </div>
                <div class="filter-group">
                    <label>Type</label>
                    <select class="filter-input" id="typeFilter">
                        <option value="all">All Types</option>
                        <option value="in-person">In-Person</option>
                        <option value="online">Online</option>
                        <option value="hybrid">Hybrid</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="events-grid" id="eventsGrid"></div>
    `;
}

function getHostPage() {
    return `
        <div class="page-header">
            <h1>Host an Event</h1>
            <p>Create memorable experiences</p>
        </div>
        <div class="prompt-library" id="promptLibrary">
            <div class="prompt-library-header">
                <span class="sparkle-icon">✨</span>
                <span>Prompt Library</span>
                <span class="prompt-subtitle">Select a template and customize the details</span>
            </div>
            <div class="prompt-templates" id="promptTemplates"></div>
        </div>
        <div class="event-form-container hidden" id="eventFormContainer">
            <div class="form-header">
                <h2 id="formTitle">New Event</h2>
                <p>Customize the details below</p>
                <button class="back-btn" id="backToTemplates">Back</button>
            </div>
            <form class="event-form" id="eventForm">
                <div class="form-group">
                    <label><span class="label-icon">✨</span> Event Name</label>
                    <input type="text" id="eventName" placeholder="Give your event a name" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea id="eventDescription" rows="4" placeholder="Describe your event..."></textarea>
                    <button type="button" class="voice-input-btn" id="voiceDescriptionBtn">
                        <span class="mic-icon">🎤</span> Record Description
                    </button>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label><span class="label-icon">📍</span> Location</label>
                        <input type="text" id="eventLocation" placeholder="Venue or Online">
                    </div>
                    <div class="form-group">
                        <label><span class="label-icon">📅</span> Date</label>
                        <input type="date" id="eventDate">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label><span class="label-icon">⏰</span> Time</label>
                        <input type="time" id="eventTime">
                    </div>
                    <div class="form-group">
                        <label><span class="label-icon">👥</span> Capacity</label>
                        <input type="number" id="eventCapacity" placeholder="Max attendees">
                    </div>
                </div>
                <div class="form-group">
                    <label>Cover Image</label>
                    <div class="image-upload" id="imageUpload">
                        <input type="file" id="coverImage" accept="image/*" hidden>
                        <div class="upload-placeholder" id="uploadPlaceholder">
                            <span class="upload-icon">🖼️</span>
                            <span>Click to upload cover image</span>
                        </div>
                        <img id="imagePreview" class="image-preview hidden" alt="Preview">
                    </div>
                </div>
                <button type="submit" class="submit-btn">
                    <span>Send to Eventflow</span>
                </button>
            </form>
        </div>
    `;
}

function getMyEventsPage() {
    return `
        <div class="page-header">
            <h1>My Events</h1>
            <p>Manage your events</p>
        </div>
        <div class="tabs">
            <button class="tab active" data-tab="hosted">Hosted</button>
            <button class="tab" data-tab="attending">Attending</button>
            <button class="tab" data-tab="saved">Saved</button>
        </div>
        <div class="tab-content active" id="hostedTab">
            <div class="my-events-list" id="hostedEvents"></div>
        </div>
        <div class="tab-content" id="attendingTab">
            <div class="my-events-list" id="attendingEvents"></div>
        </div>
        <div class="tab-content" id="savedTab">
            <div class="my-events-list" id="savedEvents"></div>
        </div>
    `;
}

function getProfilePage() {
    return `
        <div class="profile-container">
            <div class="profile-header">
                <div class="profile-avatar">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=user123" alt="Profile">
                    <div class="avatar-glow"></div>
                </div>
                <h2>${userData.name}</h2>
                <p class="profile-email">${userData.email}</p>
                <div class="profile-stats">
                    <div class="stat">
                        <span class="stat-value">${userData.hostedEvents.length}</span>
                        <span class="stat-label">Events Hosted</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${userData.attendingEvents.length}</span>
                        <span class="stat-label">Events Attended</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">234</span>
                        <span class="stat-label">Connections</span>
                    </div>
                </div>
            </div>
            <div class="profile-section">
                <h3>Preferences</h3>
                <div class="preference-item">
                    <span>Voice Assistant</span>
                    <label class="toggle">
                        <input type="checkbox" checked>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                <div class="preference-item">
                    <span>Event Notifications</span>
                    <label class="toggle">
                        <input type="checkbox" checked>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                <div class="preference-item">
                    <span>Voice Commands</span>
                    <label class="toggle">
                        <input type="checkbox" checked>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            </div>
            <button class="logout-btn" id="logoutBtn">Sign Out</button>
        </div>
    `;
}
