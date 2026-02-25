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
        attendees: 342,
        sponsorship: {
            enabled: true,
            location: "National or International",
            audienceType: "Business",
            expectedAttendance: 500,
            brandValue: 50000,
            activations: ["namingRightsStructure", "premiumBooth", "speakingMainStage", "logoMainStage", "bannerSignage"]
        }
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
        attendees: 756,
        sponsorship: {
            enabled: true,
            location: "National or International",
            audienceType: "High Net Worth",
            expectedAttendance: 1000,
            brandValue: 75000,
            activations: ["namingRightsCustom", "premiumBooth", "standardBooth", "productSampling", "speakingMainStage", "logoMainStage", "socialPostLogo", "websiteLogo"]
        }
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
        attendees: 3200,
        sponsorship: {
            enabled: true,
            location: "Province or State",
            audienceType: "General",
            expectedAttendance: 5000,
            brandValue: 60000,
            activations: ["standardBooth", "bannerSignage", "socialPostVideo", "websiteLogo", "newsletterFullPage"]
        }
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

// Sponsor purchases data
const sponsorPurchases = [
    // {
    //     id: 1,
    //     eventId: 1,
    //     sponsorName: "TechCorp Inc",
    //     sponsorEmail: "sponsor@techcorp.com",
    //     selectedActivations: ["premiumBooth", "logoMainStage"],
    //     totalPrice: 15000,
    //     purchaseDate: "2026-02-01"
    // }
];

// ============================================
// SPONSORSHIP PRICING CALCULATOR
// ============================================

// Multipliers for Property Value calculation
const sponsorshipMultipliers = {
    "General": {
        "Small Community": 0.016,
        "Province or State": 0.024,
        "National or International": 0.032
    },
    "High Net Worth": {
        "Small Community": 0.0214,
        "Province or State": 0.0323,
        "National or International": 0.0432
    },
    "Business": {
        "Small Community": 0.028,
        "Province or State": 0.042,
        "National or International": 0.056
    }
};

// Calculate Property Value
function calculatePropertyValue(brandValue, audienceType, location) {
    const multiplier = sponsorshipMultipliers[audienceType]?.[location] || 0.016;
    return brandValue * multiplier;
}

// Calculate cost for individual activation
function calculateActivationCost(activation, propertyValue, expectedAttendance) {
    // Placeholder values for social/digital metrics
    const socialFollowers = 50000;
    const webTraffic = 100000;
    const databaseSize = 10000;

    const formulas = {
        namingRightsStructure: (pv, att) => (0.0056 * pv + 0.056) * att,
        namingRightsCustom: (pv, att) => (0.0157 * pv + 0.0157) * att,
        standardBooth: (pv, att) => (0.1608 * pv + 0.1619) * att,
        premiumBooth: (pv, att) => (0.3076 * pv + 0.3097) * att,
        productSampling: (pv, att) => (0.0275 * pv + 0.0276) * att,
        speakingMainStage: (pv, att) => (1.037 * pv + 1.052) * att,
        logoMainStage: (pv, att) => (0.0284 * pv + 0.0286) * att,
        bannerSignage: (pv, att) => (0.0213 * pv + 0.0214) * att,
        socialPostLogo: (pv) => (0.0192 * pv + 0.0194) * socialFollowers,
        socialPostVideo: (pv) => (0.0231 * pv + 0.0235) * socialFollowers,
        websiteLogo: (pv) => (0.0037 * pv + 0.0037) * webTraffic,
        newsletterFullPage: (pv) => (0.0375 * pv + 0.038) * databaseSize,
        newsletterHalfPage: (pv) => (0.0212 * pv + 0.0216) * databaseSize
    };

    const formula = formulas[activation];
    if (!formula) return 0;

    return formula(propertyValue, expectedAttendance);
}

// Calculate total sponsorship price
function calculateSponsorshipPrice(event, selectedActivations) {
    if (!event.sponsorship || !event.sponsorship.enabled) {
        return { propertyValue: 0, totalCost: 0, finalPrice: 0, breakdown: {} };
    }

    const { brandValue, audienceType, location, expectedAttendance } = event.sponsorship;

    // Step 1: Calculate Property Value
    const propertyValue = calculatePropertyValue(brandValue, audienceType, location);

    // Step 2: Calculate costs for each activation
    const breakdown = {};
    let totalCost = 0;

    selectedActivations.forEach(activation => {
        const cost = calculateActivationCost(activation, propertyValue, expectedAttendance);
        breakdown[activation] = cost;
        totalCost += cost;
    });

    // Step 3: Calculate Final Price (3:1 ROI model)
    const finalPrice = totalCost / 3;

    return {
        propertyValue: Math.round(propertyValue),
        totalCost: Math.round(totalCost),
        finalPrice: Math.round(finalPrice),
        breakdown
    };
}

// Get human-readable activation names
function getActivationName(activationKey) {
    const names = {
        namingRightsStructure: "Naming Rights - Structure",
        namingRightsCustom: "Naming Rights - Custom",
        standardBooth: "Standard Booth",
        premiumBooth: "Premium Booth",
        productSampling: "Product Sampling",
        speakingMainStage: "Speaking Opportunity - Main Stage",
        logoMainStage: "Logo on Main Stage",
        bannerSignage: "Banner or Signage",
        socialPostLogo: "Social Media Post with Logo",
        socialPostVideo: "Social Media Post with Video",
        websiteLogo: "Website Logo Placement",
        newsletterFullPage: "Newsletter Ad - Full Page",
        newsletterHalfPage: "Newsletter Ad - Half Page"
    };
    return names[activationKey] || activationKey;
}

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

                <!-- Sponsorship Settings Section -->
                <div class="sponsorship-section">
                    <div class="section-header">
                        <h3><span class="label-icon">💼</span> Sponsorship Settings</h3>
                        <label class="toggle-label">
                            <input type="checkbox" id="enableSponsorship" class="toggle-checkbox">
                            <span class="toggle-text">Enable Sponsorships</span>
                        </label>
                    </div>
                    <div id="sponsorshipFields" class="sponsorship-fields hidden">
                        <div class="form-row">
                            <div class="form-group">
                                <label>Location Type</label>
                                <select id="sponsorLocation">
                                    <option value="Small Community">Small Community</option>
                                    <option value="Province or State">Province or State</option>
                                    <option value="National or International">National or International</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Audience Type</label>
                                <select id="sponsorAudienceType">
                                    <option value="General">General</option>
                                    <option value="High Net Worth">High Net Worth</option>
                                    <option value="Business">Business</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Expected Attendance</label>
                                <input type="number" id="sponsorAttendance" placeholder="Number of attendees" min="1">
                            </div>
                            <div class="form-group">
                                <label>Brand Value ($)</label>
                                <input type="number" id="sponsorBrandValue" placeholder="50000" value="50000" min="0">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Available Sponsorship Activations</label>
                            <div class="activation-grid">
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="namingRightsStructure">
                                    <span>Naming Rights - Structure</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="namingRightsCustom">
                                    <span>Naming Rights - Custom</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="standardBooth">
                                    <span>Standard Booth</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="premiumBooth">
                                    <span>Premium Booth</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="productSampling">
                                    <span>Product Sampling</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="speakingMainStage">
                                    <span>Speaking Opportunity - Main Stage</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="logoMainStage">
                                    <span>Logo on Main Stage</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="bannerSignage">
                                    <span>Banner or Signage</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="socialPostLogo">
                                    <span>Social Media Post with Logo</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="socialPostVideo">
                                    <span>Social Media Post with Video</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="websiteLogo">
                                    <span>Website Logo Placement</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="newsletterFullPage">
                                    <span>Newsletter Ad - Full Page</span>
                                </label>
                                <label class="activation-checkbox">
                                    <input type="checkbox" name="activation" value="newsletterHalfPage">
                                    <span>Newsletter Ad - Half Page</span>
                                </label>
                            </div>
                        </div>
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

function getSponsorshipsPage() {
    const sponsorableEvents = sampleEvents.filter(event =>
        event.sponsorship && event.sponsorship.enabled
    );

    return `
        <div class="page-header">
            <h1>Browse Sponsorships</h1>
            <p>Discover events looking for sponsors</p>
        </div>
        <div class="sponsorship-opportunities">
            ${sponsorableEvents.length > 0 ? `
                <div class="events-grid" id="sponsorableEventsGrid">
                    ${sponsorableEvents.map(event => `
                        <div class="event-card sponsorable-event" data-event-id="${event.id}">
                            <div class="sponsor-badge">💼 Seeking Sponsors</div>
                            <h3 class="event-card-title">${event.title}</h3>
                            <div class="event-card-meta">
                                <span>📅 ${new Date(event.date).toLocaleDateString('en-US', {
                                    month: '2-digit',
                                    day: '2-digit',
                                    year: 'numeric'
                                })}</span>
                                <span>📍 ${event.location}</span>
                            </div>
                            <div class="sponsorship-meta">
                                <span>👥 ${event.sponsorship.expectedAttendance.toLocaleString()} attendees</span>
                                <span>🎯 ${event.sponsorship.audienceType}</span>
                                <span>🌍 ${event.sponsorship.location}</span>
                            </div>
                            <div class="activation-count">
                                ${event.sponsorship.activations.length} activation${event.sponsorship.activations.length !== 1 ? 's' : ''} available
                            </div>
                            <button class="sponsor-btn" data-event-id="${event.id}">
                                View Sponsorship Options
                            </button>
                        </div>
                    `).join('')}
                </div>
            ` : `
                <div class="empty-state">
                    <div class="empty-icon">💼</div>
                    <h3>No Sponsorship Opportunities Yet</h3>
                    <p>Check back later for events seeking sponsors</p>
                </div>
            `}
        </div>
    `;
}
