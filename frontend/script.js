const API = 'http://localhost:8000';

async function loadContacts() {
    const response = await fetch(`${API}/contacts`);
    const data = await response.json();
    
    if (data.contacts.length === 0) {
        document.getElementById('contacts').innerHTML = 
            '<div class="empty-state">No contacts yet. Add your first contact above!</div>';
        return;
    }
    
        document.getElementById('contacts').innerHTML =
            data.contacts.map(c => `<div class="contact" onclick="toggleContact(${c.id})">
                <div class="contact-name">${c.name}</div>
                <div class="contact-info" id="contact-${c.id}" style="display: none;">
                    <p><strong>Group:</strong> ${c.contact_group || 'friends'}</p>
                    <p><strong>WhatsApp:</strong> ${c.whatsapp_number || 'Not provided'}</p>
                    <p><strong>Last contacted:</strong> ${c.last_contact_date || '-'}</p>
                    <p><strong>Birthday:</strong> ${c.birthday || 'Not provided'}</p>
                    <p><strong>Reminder every:</strong> ${c.reminder_frequency_days} days</p>
                    <p><strong>Notes:</strong> ${c.notes || 'None'}</p>
                </div>
                <div class="contact-actions" id="actions-${c.id}" style="display: none;">
                    <button onclick="event.stopPropagation(); draftMessage(${c.id})" class="btn btn-secondary">Draft Message</button>
                    <button onclick="event.stopPropagation(); editContact(${c.id})" class="btn btn-primary">Edit</button>
                    <button onclick="event.stopPropagation(); deleteContact(${c.id})" class="btn btn-danger">Delete</button>
                </div>
            </div>`).join('');
}

async function loadReminders() {
    const response = await fetch(`${API}/reminders`);
    const data = await response.json();
    
    if (data.reminders.length === 0) {
        document.getElementById('reminders').innerHTML = 
            '<div class="empty-state">No reminders at the moment.</div>';
        return;
    }
    
        document.getElementById('reminders').innerHTML =
            data.reminders.map(r => {
                const lastContact = r.last_contact_date ? new Date(r.last_contact_date).toLocaleDateString() : 'Never';
                
                let statusText = '';
                if (r.status === 'birthday_reminder') {
                    statusText = '🎂 Birthday reminder';
                } else if (r.days_since_contact === 0) {
                    statusText = 'Never contacted';
                } else if (r.days_since_contact >= r.reminder_frequency_days) {
                    statusText = 'Overdue';
                } else {
                    statusText = 'Due soon';
                }
                
                return `<div class="reminder-item">
                    <div class="reminder-content">
                        <div class="reminder-name">${r.name}</div>
                        <div class="reminder-meta">Last contacted: ${lastContact}</div>
                        <div class="reminder-status">${statusText}</div>
                    </div>
                    <button onclick="markAsContacted(${r.id})" class="btn btn-subtle">Mark as contacted</button>
                </div>`;
            }).join('');
}

async function markAsContacted(id) {
    const today = new Date().toISOString().split('T')[0];
    await fetch(`${API}/contacts/${id}/log`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            contact_id: id,
            contact_date: today,
            method: 'whatsapp',
            notes: ''
        })
    });
    loadContacts();
    loadReminders();
}

async function deleteContact(id) {
    await fetch(`${API}/contacts/${id}`, {method: 'DELETE'});
    loadContacts();
    loadReminders();
}

async function draftMessage(contactId) {
    // Create modal for message drafting
    showDraftModal(contactId);
}

function showDraftModal(contactId) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Draft Message</h3>
                <button class="modal-close" onclick="closeDraftModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="customPrompt">Additional context (optional):</label>
                    <textarea id="customPrompt" placeholder="Add any specific context for the message..." rows="3"></textarea>
                </div>
                <div class="modal-actions">
                    <button onclick="closeDraftModal()" class="btn btn-secondary">Cancel</button>
                    <button onclick="generateMessage(${contactId})" class="btn btn-primary">Generate Message</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.getElementById('customPrompt').focus();
}

function closeDraftModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

async function generateMessage(contactId) {
    const customPrompt = document.getElementById('customPrompt').value;
    
    try {
        // Show loading state
        const generateBtn = document.querySelector('.modal-actions .btn-primary');
        const originalText = generateBtn.textContent;
        generateBtn.textContent = 'Generating...';
        generateBtn.disabled = true;
        
        const response = await fetch(`${API}/draft-message/${contactId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                custom_prompt: customPrompt || ""
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show the drafted message in the modal
            showMessageResult(data.contact_name, data.message);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Failed to draft message: ${error.message}`);
    } finally {
        // Reset button state
        const generateBtn = document.querySelector('.modal-actions .btn-primary');
        generateBtn.textContent = 'Generate Message';
        generateBtn.disabled = false;
    }
}

function showMessageResult(contactName, message) {
    const modal = document.querySelector('.modal-overlay');
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Drafted Message for ${contactName}</h3>
                <button class="modal-close" onclick="closeDraftModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="message-preview">
                    <textarea readonly rows="6" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-family: inherit; resize: vertical;">${message}</textarea>
                </div>
                <div class="modal-actions">
                    <button onclick="closeDraftModal()" class="btn btn-secondary">Close</button>
                    <button onclick="copyMessage('${message.replace(/'/g, "\\'")}')" class="btn btn-primary">Copy Message</button>
                </div>
            </div>
        </div>
    `;
}

function copyMessage(message) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(message).then(() => {
            const copyBtn = document.querySelector('.modal-actions .btn-primary');
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            copyBtn.style.background = '#28a745';
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.background = '';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Failed to copy message to clipboard');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = message;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Message copied to clipboard!');
    }
}

function toggleContact(id) {
    const contactInfo = document.getElementById(`contact-${id}`);
    const contactActions = document.getElementById(`actions-${id}`);
    
    // Don't toggle if we're in edit mode
    if (contactInfo.innerHTML.includes('edit-form')) {
        return;
    }
    
    if (contactInfo.style.display === 'none') {
        contactInfo.style.display = 'block';
        contactActions.style.display = 'block';
    } else {
        contactInfo.style.display = 'none';
        contactActions.style.display = 'none';
    }
}

async function editContact(id) {
    // Get contact data
    const response = await fetch(`${API}/contacts`);
    const data = await response.json();
    const contact = data.contacts.find(c => c.id === id);
    
    if (!contact) return;
    
    // Show edit form
    const editForm = `
        <div class="edit-form">
            <h3>Edit Contact</h3>
            <form id="editForm-${id}">
                <div class="form-group">
                    <label for="edit-name-${id}">Name *</label>
                    <input type="text" id="edit-name-${id}" value="${contact.name}" required>
                </div>
                <div class="form-group">
                    <label for="edit-whatsapp-${id}">WhatsApp Number</label>
                    <input type="text" id="edit-whatsapp-${id}" value="${contact.whatsapp_number || ''}">
                </div>
                <div class="form-group">
                    <label for="edit-birthday-${id}">Birthday</label>
                    <input type="date" id="edit-birthday-${id}" value="${contact.birthday || ''}">
                </div>
                <div class="form-group">
                    <label for="edit-frequency-${id}">Reminder Frequency</label>
                    <div class="frequency-options">
                        <button type="button" class="freq-btn ${contact.reminder_frequency_days == 7 ? 'active' : ''}" data-days="7" onclick="setEditFrequency(${id}, 7)">Weekly</button>
                        <button type="button" class="freq-btn ${contact.reminder_frequency_days == 30 ? 'active' : ''}" data-days="30" onclick="setEditFrequency(${id}, 30)">Monthly</button>
                        <button type="button" class="freq-btn ${contact.reminder_frequency_days == 90 ? 'active' : ''}" data-days="90" onclick="setEditFrequency(${id}, 90)">Quarterly</button>
                        <button type="button" class="freq-btn ${contact.reminder_frequency_days == 180 ? 'active' : ''}" data-days="180" onclick="setEditFrequency(${id}, 180)">6 months</button>
                        <button type="button" class="freq-btn ${contact.reminder_frequency_days == 'Birthday only' ? 'active' : ''}" data-days="Birthday only" onclick="setEditFrequency(${id}, 'Birthday only')">Birthday only</button>
                    </div>
                    <input type="text" id="edit-frequency-${id}" value="${contact.reminder_frequency_days}" placeholder="Or enter custom days">
                </div>
                <div class="form-group">
                    <label for="edit-group-${id}">Contact Group</label>
                    <select id="edit-group-${id}">
                        <option value="friends" ${contact.contact_group === 'friends' ? 'selected' : ''}>Friends</option>
                        <option value="family" ${contact.contact_group === 'family' ? 'selected' : ''}>Family</option>
                        <option value="work" ${contact.contact_group === 'work' ? 'selected' : ''}>Work</option>
                        <option value="acquaintances" ${contact.contact_group === 'acquaintances' ? 'selected' : ''}>Acquaintances</option>
                        <option value="other" ${contact.contact_group === 'other' ? 'selected' : ''}>Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="edit-notes-${id}">Notes</label>
                    <textarea id="edit-notes-${id}" rows="3">${contact.notes || ''}</textarea>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                    <button type="button" onclick="cancelEdit(${id})" class="btn btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    // Replace contact info with edit form
    document.getElementById(`contact-${id}`).innerHTML = editForm;
    
    // Handle form submission
    document.getElementById(`editForm-${id}`).addEventListener('submit', async (e) => {
        e.preventDefault();
        await updateContact(id);
    });
}

function cancelEdit(id) {
    loadContacts(); // Reload to show original contact info
}

function setEditFrequency(id, days) {
    // Remove active class from all buttons in this edit form
    const editForm = document.getElementById(`contact-${id}`);
    editForm.querySelectorAll('.freq-btn').forEach(btn => btn.classList.remove('active'));
    // Add active class to clicked button
    event.target.classList.add('active');
    // Update the input field
    if (days === 'Birthday only') {
        document.getElementById(`edit-frequency-${id}`).value = 'Birthday only';
        document.getElementById(`edit-frequency-${id}`).readOnly = true;
    } else {
        document.getElementById(`edit-frequency-${id}`).value = days;
        document.getElementById(`edit-frequency-${id}`).readOnly = false;
    }
    
    // Make birthday required if "Birthday only" is selected
    const birthdayField = document.getElementById(`edit-birthday-${id}`);
    if (days === 'Birthday only') {
        birthdayField.required = true;
        birthdayField.style.borderColor = '#dc3545';
    } else {
        birthdayField.required = false;
        birthdayField.style.borderColor = '#e0e0e0';
    }
}

async function updateContact(id) {
    // Validate frequency input
    const frequencyValue = document.getElementById(`edit-frequency-${id}`).value;
    let reminderFrequency;
    
    if (frequencyValue === 'Birthday only') {
        reminderFrequency = 'Birthday only';
    } else {
        const numValue = parseInt(frequencyValue);
        if (isNaN(numValue) || numValue < 1 || numValue > 365) {
            alert('Please enter a valid number between 1 and 365, or select a predefined option.');
            return;
        }
        reminderFrequency = numValue;
    }
    
    const updateData = {
        name: document.getElementById(`edit-name-${id}`).value,
        whatsapp_number: document.getElementById(`edit-whatsapp-${id}`).value,
        birthday: document.getElementById(`edit-birthday-${id}`).value,
        reminder_frequency_days: reminderFrequency,
        notes: document.getElementById(`edit-notes-${id}`).value,
        contact_group: document.getElementById(`edit-group-${id}`).value
    };
    
    const response = await fetch(`${API}/contacts/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(updateData)
    });
    
    const result = await response.json();
    
    if (result.error) {
        alert(result.error);
        return;
    }
    
    loadContacts();
    loadReminders();
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Handle frequency button clicks
    document.querySelectorAll('.freq-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll('.freq-btn').forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            // Update the input field
            if (this.dataset.days === 'Birthday only') {
                document.getElementById('frequency').value = 'Birthday only';
                document.getElementById('frequency').readOnly = true;
            } else {
                document.getElementById('frequency').value = this.dataset.days;
                document.getElementById('frequency').readOnly = false;
            }
            
            // Make birthday required if "Birthday only" is selected
            const birthdayField = document.getElementById('birthday');
            if (this.dataset.days === 'Birthday only') {
                birthdayField.required = true;
                birthdayField.style.borderColor = '#dc3545';
            } else {
                birthdayField.required = false;
                birthdayField.style.borderColor = '#e0e0e0';
            }
        });
    });
    
    // Set initial active state for Weekly button
    document.querySelector('.freq-btn[data-days="7"]').classList.add('active');
    
    // Add contact form
    document.getElementById('addForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get the radio button value
        const contactedToday = document.querySelector('input[name="contacted_today"]:checked').value;
        const today = new Date().toISOString().split('T')[0];
        
        // Validate frequency input
        const frequencyValue = document.getElementById('frequency').value;
        let reminderFrequency;
        
        if (frequencyValue === 'Birthday only') {
            reminderFrequency = 'Birthday only';
        } else {
            const numValue = parseInt(frequencyValue);
            if (isNaN(numValue) || numValue < 1 || numValue > 365) {
                alert('Please enter a valid number between 1 and 365, or select a predefined option.');
                return;
            }
            reminderFrequency = numValue;
        }
        
        // Create contact data
        const contactData = {
            name: document.getElementById('name').value,
            whatsapp_number: document.getElementById('whatsapp').value,
            birthday: document.getElementById('birthday').value,
            reminder_frequency_days: reminderFrequency,
            notes: document.getElementById('notes').value,
            last_contact_date: contactedToday === 'yes' ? today : null,
            contact_group: document.getElementById('group').value
        };
        
        const response = await fetch(`${API}/contacts`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(contactData)
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert(result.error);
            return;
        }
        
        // Clear the form
        document.getElementById('addForm').reset();
        document.querySelector('input[name="contacted_today"][value="yes"]').checked = true;
        
        loadContacts();
        loadReminders();
    });
    
    // Load initial data
    loadContacts();
    loadReminders();
});
