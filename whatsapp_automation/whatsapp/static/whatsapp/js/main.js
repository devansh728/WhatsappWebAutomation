// Main JavaScript for WhatsApp Automation

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize date pickers
    const datePickers = document.querySelectorAll('.datepicker');
    if (datePickers.length > 0) {
        datePickers.forEach(picker => {
            picker.addEventListener('focus', function() {
                this.type = 'date';
            });
            picker.addEventListener('blur', function() {
                if (!this.value) {
                    this.type = 'text';
                }
            });
        });
    }

    // Handle filter form submission
    const filterForms = document.querySelectorAll('.filter-form');
    if (filterForms.length > 0) {
        filterForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                // Remove empty fields before submitting
                const inputs = form.querySelectorAll('input, select');
                inputs.forEach(input => {
                    if (!input.value) {
                        input.disabled = true;
                    }
                });
                // Form will submit normally
            });
        });
    }

    // Handle message row click to navigate to detail page
    const messageRows = document.querySelectorAll('.message-row');
    if (messageRows.length > 0) {
        messageRows.forEach(row => {
            row.addEventListener('click', function() {
                const url = this.dataset.url;
                if (url) {
                    window.location.href = url;
                }
            });
        });
    }

    // Function to fetch messages via API for React components
    window.fetchMessages = async function(params = {}) {
        const queryParams = new URLSearchParams(params);
        const response = await fetch(`/whatsapp/api/messages/?${queryParams}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    };

    // Function to fetch chat summary via API for React components
    window.fetchChatSummary = async function() {
        const response = await fetch('/whatsapp/api/summary/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    };

    // Initialize React components if present
    initializeReactComponents();
});

function initializeReactComponents() {
    // Dashboard Stats Component
    const dashboardStats = document.getElementById('react-dashboard-stats');
    if (dashboardStats) {
        renderDashboardStats(dashboardStats);
    }

    // Message List Component
    const reactMessageList = document.getElementById('react-message-list');
    if (reactMessageList) {
        renderMessageList(reactMessageList);
    }
}

// React component for Dashboard Stats
function renderDashboardStats(container) {
    // Define the React component
    const DashboardStats = () => {
        const [loading, setLoading] = React.useState(true);
        const [stats, setStats] = React.useState(null);
        const [error, setError] = React.useState(null);

        React.useEffect(() => {
            fetchChatSummary()
                .then(data => {
                    setStats(data);
                    setLoading(false);
                })
                .catch(err => {
                    setError(err.message);
                    setLoading(false);
                });
        }, []);

        if (loading) {
            return (
                <div className="text-center py-5">
                    <div className="spinner-border text-success" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                </div>
            );
        }

        if (error) {
            return (
                <div className="alert alert-danger" role="alert">
                    Error loading data: {error}
                </div>
            );
        }

        return (
            <div className="row">
                <div className="col-md-3 mb-4">
                    <div className="card stat-card dashboard-card h-100">
                        <div className="card-body">
                            <h5 className="card-title text-muted">Total Messages</h5>
                            <h2 className="display-4 fw-bold text-success">{stats.stats.total_messages}</h2>
                        </div>
                    </div>
                </div>
                <div className="col-md-3 mb-4">
                    <div className="card stat-card dashboard-card h-100">
                        <div className="card-body">
                            <h5 className="card-title text-muted">Unique Senders</h5>
                            <h2 className="display-4 fw-bold text-success">{stats.stats.total_senders}</h2>
                        </div>
                    </div>
                </div>
                <div className="col-md-3 mb-4">
                    <div className="card stat-card dashboard-card h-100">
                        <div className="card-body">
                            <h5 className="card-title text-muted">Unique Receivers</h5>
                            <h2 className="display-4 fw-bold text-success">{stats.stats.total_receivers}</h2>
                        </div>
                    </div>
                </div>
                <div className="col-md-3 mb-4">
                    <div className="card stat-card dashboard-card h-100">
                        <div className="card-body">
                            <h5 className="card-title text-muted">Media Files</h5>
                            <h2 className="display-4 fw-bold text-success">{stats.stats.total_media}</h2>
                        </div>
                    </div>
                </div>
                
                <div className="col-md-12 mt-4">
                    <div className="card dashboard-card">
                        <div className="card-header bg-success text-white">
                            <h5 className="mb-0">Top Active Chats</h5>
                        </div>
                        <div className="card-body">
                            <div className="table-responsive">
                                <table className="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Sender</th>
                                            <th>Receiver</th>
                                            <th>Message Count</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {stats.top_chats.map((chat, index) => (
                                            <tr key={index}>
                                                <td>{chat.sender}</td>
                                                <td>{chat.receiver}</td>
                                                <td>{chat.count}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    // Render the component
    ReactDOM.render(<DashboardStats />, container);
}

// React component for Message List
function renderMessageList(container) {
    // Define the React component
    const MessageList = () => {
        const [messages, setMessages] = React.useState([]);
        const [loading, setLoading] = React.useState(true);
        const [error, setError] = React.useState(null);
        const [page, setPage] = React.useState(1);
        const [hasMore, setHasMore] = React.useState(true);
        const messagesPerPage = 10;

        const loadMessages = (pageNum) => {
            setLoading(true);
            fetchMessages({
                offset: (pageNum - 1) * messagesPerPage,
                limit: messagesPerPage
            })
                .then(data => {
                    if (data.messages.length < messagesPerPage) {
                        setHasMore(false);
                    }
                    if (pageNum === 1) {
                        setMessages(data.messages);
                    } else {
                        setMessages(prevMessages => [...prevMessages, ...data.messages]);
                    }
                    setLoading(false);
                })
                .catch(err => {
                    setError(err.message);
                    setLoading(false);
                });
        };

        React.useEffect(() => {
            loadMessages(page);
        }, [page]);

        const loadMore = () => {
            setPage(prevPage => prevPage + 1);
        };

        if (error) {
            return (
                <div className="alert alert-danger" role="alert">
                    Error loading messages: {error}
                </div>
            );
        }

        return (
            <div className="react-message-container">
                {messages.map(message => (
                    <div key={message.id} className={`message-bubble ${message.sender === 'You' ? 'message-outgoing' : 'message-incoming'}`}>
                        <div className="message-sender">{message.sender}</div>
                        <div className="message-text">{message.message}</div>
                        <div className="message-meta">
                            {new Date(message.timestamp).toLocaleString()}
                            {message.has_media && (
                                <span className="ms-2">
                                    <i className="fas fa-paperclip"></i>
                                </span>
                            )}
                        </div>
                    </div>
                ))}
                
                {loading && (
                    <div className="text-center my-3">
                        <div className="spinner-border spinner-border-sm text-success" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                    </div>
                )}
                
                {hasMore && !loading && (
                    <div className="text-center mt-3 mb-5">
                        <button className="btn btn-outline-success" onClick={loadMore}>
                            Load More
                        </button>
                    </div>
                )}
                
                {!hasMore && messages.length > 0 && (
                    <div className="text-center text-muted mt-3 mb-5">
                        No more messages to load
                    </div>
                )}
                
                {!loading && messages.length === 0 && (
                    <div className="alert alert-info" role="alert">
                        No messages found
                    </div>
                )}
            </div>
        );
    };

    // Render the component
    ReactDOM.render(<MessageList />, container);
} 