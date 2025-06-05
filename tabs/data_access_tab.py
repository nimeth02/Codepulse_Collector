from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea

def setup_data_access_tab(parent):
    """Create the Data Access Documentation tab"""
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    # Create scroll area for long content
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    content = QWidget()
    content_layout = QVBoxLayout(content)
    
    # Title
    title = QLabel("GitHub Data Access Documentation")
    title.setStyleSheet("font-size: 16px; font-weight: bold;")
    content_layout.addWidget(title)
    
    # Documentation text
    doc_text = QTextEdit()
    doc_text.setReadOnly(True)
    doc_text.setHtml(get_documentation_html())
    content_layout.addWidget(doc_text)
    
    scroll.setWidget(content)
    layout.addWidget(scroll)
    return tab

def get_documentation_html():
    """Return formatted HTML documentation"""
    return """
    <h2>Data Collection Overview</h2>
    <p>This application collects the following GitHub data to measure developer productivity and efficiency:</p>
    
    <h3>1. User Data</h3>
    <ul>
        <li><b>Username:</b> GitHub login name (e.g., "octocat")</li>
        <li><b>Node ID:</b> GitHub's internal identifier</li>
        <li><b>Avatar URL:</b> Link to profile picture (optional)</li>
        <li><b>Display Name:</b> User's public profile name</li>
        <li><b>Account Dates:</b> Creation and last update timestamps</li>
    </ul>
    
    <h3>2. Project Data</h3>
    <ul>
        <li><b>Project Name:</b> Repository or project name</li>
        <li><b>Node ID:</b> GitHub's internal identifier</li>
        <li><b>Avatar URL:</b> Project/repository image (optional)</li>
        <li><b>Display Name:</b> Human-readable project name</li>
        <li><b>Timestamps:</b> Creation and update dates</li>
    </ul>
    
    <h3>3. Team Data</h3>
    <ul>
        <li><b>Team Name:</b> Organization team name</li>
        <li><b>Description:</b> Team purpose/description (optional)</li>
        <li><b>Node ID:</b> GitHub's internal identifier</li>
    </ul>
    
    <h3>4. Repository Data</h3>
    <ul>
        <li><b>Repository Name:</b> Code repository name</li>
        <li><b>Full Name:</b> Organization/repo format</li>
        <li><b>Default Branch:</b> Typically "main" or "master"</li>
        <li><b>Node ID:</b> GitHub's internal identifier</li>
    </ul>
    
    <h3>5. Pull Request Data</h3>
    <ul>
        <li><b>Basic Metadata:</b> PR number, title, description</li>
        <li><b>State:</b> Open, closed, merged</li>
        <li><b>Branch Info:</b> Source and target branches</li>
        <li><b>Code Metrics:</b> Commits, additions, deletions, changed files</li>
        <li><b>Timestamps:</b> Creation, update, merge/close dates</li>
    </ul>
    
    <h2>Data Storage & Privacy</h2>
    <p>All collected data is stored in our secure database with the following protections:</p>
    <ul>
        <li>Encrypted at rest</li>
        <li>Access restricted to authorized personnel</li>
        <li>Retention period: 1 year unless otherwise specified</li>
    </ul>
    
    <h2>What We Don't Collect</h2>
    <ul>
        <li>Private repository content (unless explicitly granted access)</li>
        <li>User passwords or authentication tokens</li>
        <li>Email addresses (unless publicly visible on GitHub profile)</li>
    </ul>
    
    <h2>Purpose of Collection</h2>
    <p>This data helps us:</p>
    <ul>
        <li>Measure team productivity</li>
        <li>Identify collaboration patterns</li>
        <li>Improve development workflows</li>
        <li>Allocate resources effectively</li>
    </ul>
    """