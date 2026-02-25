/**
 * EVENTFLOW - AI-Powered Event Platform
 * Application Logic - Part 2
 */

// ============================================
// EVENT CARD RENDERER
// ============================================

function renderEventCard(event, showLink = true) {
    const formattedDate = new Date(event.date).toLocaleDateString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric'
    });

    return `
        <div class="event-card" data-event-id="${event.id}">
            ${showLink ? `<a href="#" class="event-card-link" title="View details">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
            </a>` : ''}
            <h3 class="event-card-title">${event.title}</h3>
            <div class="event-card-meta">
                <span>📅 ${formattedDate} at ${event.time}</span>
                <span>📍 ${event.location}</span>
            </div>
            <div class="event-card-tags">
                <span class="event-tag category">${event.category}</span>
                <span class="event-tag price">$ $${event.price}</span>
                <span class="event-tag platform">${event.platform}</span>
            </div>
        </div>
    `;
}

// ============================================
// NAVIGATION
// ============================================

function navigateTo(page) {
    state.currentPage = page;

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
    });

    // Render page content
    let content = '';
    switch (page) {
        case 'home':
            content = getHomePage();
            break;
        case 'discover':
            content = getDiscoverPage();
            break;
        case 'host':
            content = getHostPage();
            break;
        case 'sponsorships':
            content = getSponsorshipsPage();
            break;
        case 'my-events':
            content = getMyEventsPage();
            break;
        case 'profile':
            content = getProfilePage();
            break;
    }

    elements.mainContent.innerHTML = content;

    // Initialize page-specific functionality
    setTimeout(() => {
        initPageHandlers(page);
    }, 100);

    // Close mobile menu
    elements.sideNav.classList.remove('open');
    elements.mobileMenuBtn.classList.remove('active');
}

function initPageHandlers(page) {
    switch (page) {
        case 'home':
            initHomePage();
            break;
        case 'discover':
            initDiscoverPage();
            break;
        case 'host':
            initHostPage();
            break;
        case 'sponsorships':
            initSponsorshipsPage();
            break;
        case 'my-events':
            initMyEventsPage();
            break;
        case 'profile':
            initProfilePage();
            break;
    }
}

// ============================================
// HOME PAGE
// ============================================

function initHomePage() {
    const orbContainer = document.getElementById('orbContainer');

    if (orbContainer) {
        orbContainer.addEventListener('click', () => {
            startVoiceListening();
        });
    }
}

function showAIResponse(query, events) {
    const responseCard = document.getElementById('responseCard');
    const responseContent = document.getElementById('responseContent');
    const eventsResults = document.getElementById('eventsResults');
    const resultsHeader = document.getElementById('resultsHeader');
    const eventsList = document.getElementById('eventsList');

    if (!responseCard) return;

    // Show analysis
    responseCard.classList.remove('hidden');
    responseContent.textContent = `Found ${events.length} events across 1 categories (${events[0]?.category || 'various'}). Dates range ${events.length > 0 ? events[0].date : 'N/A'} to ${events.length > 0 ? events[events.length - 1].date : 'N/A'}. Platforms: eventbrite & luma.`;

    // Show events
    eventsResults.classList.remove('hidden');
    resultsHeader.innerHTML = `
        <span>🔮</span> Eventflow found ${events.length} events - ${events[0]?.title || 'Various events'} and ${events.length - 1} more
    `;

    eventsList.innerHTML = events.map(event => renderEventCard(event)).join('');

    // Add click handlers
    eventsList.querySelectorAll('.event-card').forEach(card => {
        card.addEventListener('click', () => {
            const eventId = parseInt(card.dataset.eventId);
            showEventModal(eventId);
        });
    });
}

// ============================================
// DISCOVER PAGE
// ============================================

function initDiscoverPage() {
    renderEventsGrid('all');

    // Filter chips
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            state.currentFilter = chip.dataset.filter;
            renderEventsGrid(state.currentFilter);
        });
    });
}

function renderEventsGrid(filter) {
    const grid = document.getElementById('eventsGrid');
    if (!grid) return;

    let filtered = sampleEvents;
    if (filter !== 'all') {
        filtered = sampleEvents.filter(e => e.category === filter);
    }

    grid.innerHTML = filtered.map(event => renderEventCard(event)).join('');

    // Add click handlers
    grid.querySelectorAll('.event-card').forEach(card => {
        card.addEventListener('click', () => {
            const eventId = parseInt(card.dataset.eventId);
            showEventModal(eventId);
        });
    });
}

// ============================================
// HOST PAGE
// ============================================

function initHostPage() {
    const templatesContainer = document.getElementById('promptTemplates');
    const promptLibrary = document.getElementById('promptLibrary');
    const eventFormContainer = document.getElementById('eventFormContainer');
    const backBtn = document.getElementById('backToTemplates');
    const eventForm = document.getElementById('eventForm');
    const imageUpload = document.getElementById('imageUpload');
    const coverImage = document.getElementById('coverImage');
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const voiceDescBtn = document.getElementById('voiceDescriptionBtn');

    // Render templates
    if (templatesContainer) {
        templatesContainer.innerHTML = promptTemplates.map(template => `
            <div class="prompt-template" data-template-id="${template.id}">
                <div class="prompt-template-header">
                    <h3>${template.title}</h3>
                    <span class="prompt-template-tag">${template.tag}</span>
                </div>
                <p>${template.description}</p>
                <div class="prompt-template-meta">
                    <span>📍 ${template.location}</span>
                    <span>⏰ ${template.time}</span>
                </div>
            </div>
        `).join('');

        // Template selection
        templatesContainer.querySelectorAll('.prompt-template').forEach(template => {
            template.addEventListener('click', () => {
                const templateId = parseInt(template.dataset.templateId);
                selectTemplate(templateId);
            });
        });
    }

    // Back button
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            promptLibrary.classList.remove('hidden');
            eventFormContainer.classList.add('hidden');
            state.selectedTemplate = null;
        });
    }

    // Image upload
    if (imageUpload) {
        imageUpload.addEventListener('click', () => coverImage.click());
        coverImage.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.src = e.target.result;
                    imagePreview.classList.remove('hidden');
                    uploadPlaceholder.classList.add('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Voice description
    if (voiceDescBtn) {
        voiceDescBtn.addEventListener('click', () => {
            startVoiceListening((transcript) => {
                document.getElementById('eventDescription').value = transcript;
            });
        });
    }

    // Sponsorship toggle
    const enableSponsorship = document.getElementById('enableSponsorship');
    const sponsorshipFields = document.getElementById('sponsorshipFields');

    if (enableSponsorship && sponsorshipFields) {
        enableSponsorship.addEventListener('change', (e) => {
            if (e.target.checked) {
                sponsorshipFields.classList.remove('hidden');
            } else {
                sponsorshipFields.classList.add('hidden');
            }
        });
    }

    // Form submission
    if (eventForm) {
        eventForm.addEventListener('submit', (e) => {
            e.preventDefault();

            // Collect sponsorship data if enabled
            const sponsorshipEnabled = enableSponsorship?.checked || false;
            let sponsorshipData = null;

            if (sponsorshipEnabled) {
                const selectedActivations = Array.from(
                    document.querySelectorAll('input[name="activation"]:checked')
                ).map(cb => cb.value);

                sponsorshipData = {
                    enabled: true,
                    location: document.getElementById('sponsorLocation').value,
                    audienceType: document.getElementById('sponsorAudienceType').value,
                    expectedAttendance: parseInt(document.getElementById('sponsorAttendance').value) || 0,
                    brandValue: parseInt(document.getElementById('sponsorBrandValue').value) || 50000,
                    activations: selectedActivations
                };
            }

            // Here you would normally save the event with sponsorshipData
            // For now, just show success message
            showToast('Event created successfully!', 'success');
            navigateTo('my-events');
        });
    }
}

function selectTemplate(templateId) {
    const template = promptTemplates.find(t => t.id === templateId);
    if (!template) return;

    state.selectedTemplate = template;

    const promptLibrary = document.getElementById('promptLibrary');
    const eventFormContainer = document.getElementById('eventFormContainer');
    const formTitle = document.getElementById('formTitle');

    promptLibrary.classList.add('hidden');
    eventFormContainer.classList.remove('hidden');
    formTitle.textContent = template.title;

    // Pre-fill form
    document.getElementById('eventName').value = template.title;
    document.getElementById('eventDescription').value = template.description;
    document.getElementById('eventLocation').value = template.location;
}

// ============================================
// MY EVENTS PAGE
// ============================================

function initMyEventsPage() {
    renderMyEvents();

    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(`${tab.dataset.tab}Tab`).classList.add('active');
        });
    });
}

function renderMyEvents() {
    const hostedContainer = document.getElementById('hostedEvents');
    const attendingContainer = document.getElementById('attendingEvents');
    const savedContainer = document.getElementById('savedEvents');

    const renderList = (container, eventIds) => {
        if (!container) return;
        const events = sampleEvents.filter(e => eventIds.includes(e.id));
        if (events.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-state-icon">📭</span>
                    <p>No events here yet</p>
                </div>
            `;
        } else {
            container.innerHTML = events.map(e => renderEventCard(e)).join('');
            container.querySelectorAll('.event-card').forEach(card => {
                card.addEventListener('click', () => {
                    showEventModal(parseInt(card.dataset.eventId));
                });
            });
        }
    };

    renderList(hostedContainer, userData.hostedEvents);
    renderList(attendingContainer, userData.attendingEvents);
    renderList(savedContainer, userData.savedEvents);
}

// ============================================
// PROFILE PAGE
// ============================================

function initProfilePage() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            showToast('Signed out successfully', 'success');
        });
    }
}

function initSponsorshipsPage() {
    console.log('Initializing sponsorships page');
    // Attach event listeners to sponsor buttons
    const sponsorButtons = document.querySelectorAll('.sponsor-btn');
    console.log('Found sponsor buttons:', sponsorButtons.length);
    sponsorButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const eventId = parseInt(btn.dataset.eventId);
            console.log('Clicked sponsor button for event:', eventId);
            showSponsorshipModal(eventId);
        });
    });
}

// ============================================
// SPONSORSHIP MODAL
// ============================================

function showSponsorshipModal(eventId) {
    console.log('showSponsorshipModal called with eventId:', eventId);
    const event = sampleEvents.find(e => e.id === eventId);
    console.log('Found event:', event);
    if (!event || !event.sponsorship || !event.sponsorship.enabled) {
        console.log('Event not found or sponsorship not enabled');
        return;
    }

    // Create modal if it doesn't exist
    let modal = document.getElementById('sponsorshipModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'sponsorshipModal';
        modal.className = 'modal';
        document.body.appendChild(modal);
    }

    const { sponsorship } = event;
    const activations = sponsorship.activations;

    // Build activation checkboxes grouped by category
    const activationCategories = {
        'Naming Rights': ['namingRightsStructure', 'namingRightsCustom'],
        'Booths': ['standardBooth', 'premiumBooth', 'productSampling'],
        'Stage & Visibility': ['speakingMainStage', 'logoMainStage', 'bannerSignage'],
        'Digital & Media': ['socialPostLogo', 'socialPostVideo', 'websiteLogo', 'newsletterFullPage', 'newsletterHalfPage']
    };

    let categoriesHtml = '';
    for (const [category, keys] of Object.entries(activationCategories)) {
        const categoryActivations = keys.filter(k => activations.includes(k));
        if (categoryActivations.length > 0) {
            categoriesHtml += `
                <div class="activation-category">
                    <h4>${category}</h4>
                    <div class="activation-options">
                        ${categoryActivations.map(key => `
                            <label class="activation-option">
                                <input type="checkbox" class="sponsor-activation-checkbox" value="${key}">
                                <span>${getActivationName(key)}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    modal.innerHTML = `
        <div class="modal-backdrop" id="sponsorModalBackdrop"></div>
        <div class="modal-content sponsorship-modal-content">
            <button class="modal-close" id="closeSponsorModal">&times;</button>
            <h2>${event.title}</h2>
            <div class="sponsorship-event-info">
                <div class="info-row">
                    <span><strong>Date:</strong> ${new Date(event.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
                    <span><strong>Location:</strong> ${event.location}</span>
                </div>
                <div class="info-row">
                    <span><strong>Expected Attendance:</strong> ${sponsorship.expectedAttendance.toLocaleString()}</span>
                    <span><strong>Audience:</strong> ${sponsorship.audienceType}</span>
                </div>
            </div>

            <h3>Select Your Sponsorship Activations</h3>
            <div class="activation-categories" id="activationCategories">
                ${categoriesHtml}
            </div>

            <div class="pricing-calculator" id="pricingCalculator">
                <h3>Your Sponsorship Investment</h3>
                <div class="pricing-breakdown">
                    <div class="pricing-row">
                        <span>Property Value:</span>
                        <span id="propertyValue">$0</span>
                    </div>
                    <div class="pricing-row">
                        <span>Total Marketing Value:</span>
                        <span id="totalCost">$0</span>
                    </div>
                    <div class="pricing-row final-price">
                        <span>Your Investment:</span>
                        <span id="finalPrice">$0</span>
                    </div>
                    <div class="roi-explanation">
                        <span class="roi-badge">3:1 ROI</span>
                        <p>You receive <strong id="roiValue">$0</strong> in marketing value for your investment</p>
                    </div>
                </div>
                <div class="selected-activations" id="selectedActivations">
                    <h4>Selected Activations:</h4>
                    <ul id="selectedActivationsList"></ul>
                </div>
            </div>

            <button class="submit-btn purchase-sponsor-btn" id="purchaseSponsorBtn" disabled>
                Purchase Sponsorship
            </button>
        </div>
    `;

    modal.classList.add('active');

    // Attach close modal event listeners
    const closeBtn = document.getElementById('closeSponsorModal');
    const backdrop = document.getElementById('sponsorModalBackdrop');

    if (closeBtn) {
        closeBtn.addEventListener('click', closeSponsorshipModal);
    }
    if (backdrop) {
        backdrop.addEventListener('click', closeSponsorshipModal);
    }

    // Attach event listeners for checkboxes
    const checkboxes = modal.querySelectorAll('.sponsor-activation-checkbox');
    checkboxes.forEach(cb => {
        cb.addEventListener('change', () => updateSponsorshipPricing(event));
    });

    // Initial pricing calculation (with no selections)
    updateSponsorshipPricing(event);
}

function updateSponsorshipPricing(event) {
    const checkboxes = document.querySelectorAll('.sponsor-activation-checkbox:checked');
    const selectedActivations = Array.from(checkboxes).map(cb => cb.value);

    const pricing = calculateSponsorshipPrice(event, selectedActivations);

    // Update displayed values
    document.getElementById('propertyValue').textContent = `$${pricing.propertyValue.toLocaleString()}`;
    document.getElementById('totalCost').textContent = `$${pricing.totalCost.toLocaleString()}`;
    document.getElementById('finalPrice').textContent = `$${pricing.finalPrice.toLocaleString()}`;
    document.getElementById('roiValue').textContent = `$${pricing.totalCost.toLocaleString()}`;

    // Update selected activations list
    const activationsList = document.getElementById('selectedActivationsList');
    if (selectedActivations.length > 0) {
        activationsList.innerHTML = selectedActivations.map(key =>
            `<li>${getActivationName(key)}: $${Math.round(pricing.breakdown[key]).toLocaleString()}</li>`
        ).join('');
    } else {
        activationsList.innerHTML = '<li class="empty">No activations selected</li>';
    }

    // Enable/disable purchase button
    const purchaseBtn = document.getElementById('purchaseSponsorBtn');
    if (purchaseBtn) {
        purchaseBtn.disabled = selectedActivations.length === 0;
    }

    // Add purchase handler
    if (purchaseBtn && !purchaseBtn.dataset.listenerAttached) {
        purchaseBtn.dataset.listenerAttached = 'true';
        purchaseBtn.addEventListener('click', () => {
            if (selectedActivations.length > 0) {
                // Here you would normally process the purchase
                sponsorPurchases.push({
                    id: sponsorPurchases.length + 1,
                    eventId: event.id,
                    sponsorName: "Demo Sponsor",
                    sponsorEmail: "sponsor@example.com",
                    selectedActivations: selectedActivations,
                    totalPrice: pricing.finalPrice,
                    purchaseDate: new Date().toISOString().split('T')[0]
                });

                showToast('Sponsorship purchased successfully!', 'success');
                closeSponsorshipModal();
            }
        });
    }
}

function closeSponsorshipModal() {
    const modal = document.getElementById('sponsorshipModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// ============================================
// EVENT MODAL
// ============================================

function showEventModal(eventId) {
    const event = sampleEvents.find(e => e.id === eventId);
    if (!event) return;

    const modalBody = elements.eventModalBody;
    modalBody.innerHTML = `
        <button class="modal-close" onclick="closeEventModal()">&times;</button>
        <h2 style="font-size: 28px; font-weight: 700; margin-bottom: 16px;">${event.title}</h2>
        <div style="display: flex; gap: 16px; margin-bottom: 20px; color: var(--text-muted); font-size: 14px;">
            <span>📅 ${new Date(event.date).toLocaleDateString()}</span>
            <span>⏰ ${event.time}</span>
            <span>📍 ${event.location}</span>
        </div>
        <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 24px;">${event.description}</p>
        <div style="display: flex; gap: 12px; margin-bottom: 24px;">
            <span class="event-tag category">${event.category}</span>
            <span class="event-tag price">$${event.price}</span>
            <span class="event-tag platform">${event.platform}</span>
        </div>
        <div style="background: var(--bg-card); border-radius: 12px; padding: 16px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: var(--text-muted);">Capacity</span>
                <span>${event.attendees} / ${event.capacity}</span>
            </div>
            <div style="height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: ${(event.attendees / event.capacity) * 100}%; background: var(--gradient-purple); border-radius: 4px;"></div>
            </div>
        </div>
        <div style="display: flex; gap: 12px;">
            <button class="submit-btn" style="flex: 1;" onclick="rsvpEvent(${event.id})">RSVP / Join Event</button>
            <button style="padding: 14px 20px; background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; color: var(--text-primary); cursor: pointer;" onclick="saveEvent(${event.id})">💾 Save</button>
        </div>
    `;

    elements.eventModal.classList.add('active');
}

function closeEventModal() {
    elements.eventModal.classList.remove('active');
}

function rsvpEvent(eventId) {
    showToast('Successfully registered for event!', 'success');
    closeEventModal();
}

function saveEvent(eventId) {
    showToast('Event saved to your list!', 'success');
}

// ============================================
// VOICE FEATURES
// ============================================

let recognition = null;
let voiceCallback = null;

function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            elements.voiceTranscript.textContent = transcript;
        };

        recognition.onend = () => {
            stopVoiceListening();
            const transcript = elements.voiceTranscript.textContent;
            if (transcript && voiceCallback) {
                voiceCallback(transcript);
            } else if (transcript) {
                processVoiceCommand(transcript);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            stopVoiceListening();
            showToast('Voice recognition failed. Please try again.', 'error');
        };
    }
}

function startVoiceListening(callback = null) {
    voiceCallback = callback;

    if (recognition) {
        state.isListening = true;
        elements.voiceOverlay.classList.remove('hidden');
        elements.voiceTranscript.textContent = '';
        elements.voiceBtn.classList.add('active');
        recognition.start();
    } else {
        // Simulate voice for browsers without support
        showToast('Voice recognition not supported. Using text input instead.', 'error');
        openChatModal();
    }
}

function stopVoiceListening() {
    state.isListening = false;
    elements.voiceOverlay.classList.add('hidden');
    elements.voiceBtn.classList.remove('active');
    if (recognition) {
        recognition.stop();
    }
}

function processVoiceCommand(transcript) {
    const lower = transcript.toLowerCase();

    // Navigation commands
    if (lower.includes('discover') || lower.includes('find events') || lower.includes('search')) {
        navigateTo('discover');
        return;
    }
    if (lower.includes('host') || lower.includes('create event')) {
        navigateTo('host');
        return;
    }
    if (lower.includes('sponsor') || lower.includes('sponsorship')) {
        navigateTo('sponsorships');
        return;
    }
    if (lower.includes('my events') || lower.includes('my schedule')) {
        navigateTo('my-events');
        return;
    }
    if (lower.includes('profile') || lower.includes('settings')) {
        navigateTo('profile');
        return;
    }
    if (lower.includes('home') || lower.includes('go back')) {
        navigateTo('home');
        return;
    }

    // Event search
    let filtered = sampleEvents;
    if (lower.includes('tech')) {
        filtered = sampleEvents.filter(e => e.category === 'tech');
    } else if (lower.includes('music')) {
        filtered = sampleEvents.filter(e => e.category === 'music');
    } else if (lower.includes('business')) {
        filtered = sampleEvents.filter(e => e.category === 'business');
    } else if (lower.includes('sports')) {
        filtered = sampleEvents.filter(e => e.category === 'sports');
    }

    if (state.currentPage === 'home') {
        showAIResponse(transcript, filtered);
    } else {
        navigateTo('home');
        setTimeout(() => showAIResponse(transcript, filtered), 300);
    }
}

// ============================================
// CHAT MODAL
// ============================================

function openChatModal() {
    elements.chatModal.classList.add('active');
    elements.chatInput.focus();
}

function closeChatModal() {
    elements.chatModal.classList.remove('active');
    elements.chatInput.value = '';
}

function sendChatMessage() {
    const message = elements.chatInput.value.trim();
    if (!message) return;

    closeChatModal();
    processVoiceCommand(message);
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${type === 'success' ? '✅' : '❌'}</span>
        <span class="toast-message">${message}</span>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// EVENT LISTENERS
// ============================================

function initEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navigateTo(link.dataset.page);
        });
    });

    // Mobile menu
    elements.mobileMenuBtn.addEventListener('click', () => {
        elements.mobileMenuBtn.classList.toggle('active');
        elements.sideNav.classList.toggle('open');
    });

    // Notification toggle
    elements.notificationToggle.addEventListener('click', () => {
        elements.notificationBar.classList.toggle('hidden');
    });

    // Voice button
    elements.voiceBtn.addEventListener('click', () => {
        if (state.isListening) {
            stopVoiceListening();
        } else {
            startVoiceListening();
        }
    });

    // Chat button
    elements.chatBtn.addEventListener('click', openChatModal);

    // Chat modal
    elements.cancelChat.addEventListener('click', closeChatModal);
    elements.sendChat.addEventListener('click', sendChatMessage);
    elements.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

    // Modal backdrops
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', () => {
            closeChatModal();
            closeEventModal();
        });
    });

    // Stop listening button
    elements.stopListening.addEventListener('click', stopVoiceListening);
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    initVoiceRecognition();
    navigateTo('home');
});
