import re

# Read the original file
with open(r'c:\BIG HACK\tax-fraud-gnn\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the chatbot route
content = re.sub(r'@app\.route\("/chatbot"\)\s*def chatbot\(\):\s*"""Chatbot route - serves the chatbot interface"""\s*return render_template\("chatbot\.html"\)\s*\n\s*\n', '', content)

# Remove the chatbot API routes and functions
content = re.sub(r'@app\.route\("/api/chatbot/stats"\)[\s\S]*?@app\.route\("/api/companies"\)', '@app.route("/api/companies")', content, count=1)

# Remove the chatbot reset route
content = re.sub(r'@app\.route\("/api/chatbot/reset", methods=\["POST"\]\)[\s\S]*?def chatbot_reset\(\):[\s\S]*?return jsonify\({"status": "success"}\)\s*\n\s*except Exception as e:\s*\n\s*logger\.error\(f"Error in chatbot_reset: {e}"\)\s*\n\s*return jsonify\({"error": str\(e\)}\), 500\s*\n\s*\n', '', content)

# Remove the get_chatbot_statistics_context function
content = re.sub(r'def get_chatbot_statistics_context\(\):\s*"""Helper function to get statistics context for chatbot"""[\s\S]*?return "Error retrieving statistics"\s*\n', '', content)

# Write the modified content back to the file
with open(r'c:\BIG HACK\tax-fraud-gnn\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Chatbot code removed successfully!")