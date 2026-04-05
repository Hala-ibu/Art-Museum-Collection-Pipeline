from urllib.robotparser import RobotFileParser

def check_robots(base_url, path="/", user_agent="ResearchBot/1.0"):
    robots_url = base_url.rstrip("/") + "/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    
    try:
        rp.read()
        
        full_url = base_url.rstrip("/") + path
        allowed = rp.can_fetch(user_agent, full_url)

        print(f"Checking robots.txt: {robots_url}")
        if allowed:
            print(f" Path '{path}' is ALLOWED for {user_agent}")
        else:
            print(f" Path '{path}' is DISALLOWED for {user_agent}")
            
        return allowed
    except Exception as e:
        print(f"Could not read robots.txt: {e}")
        return False

if __name__ == "__main__":
    base = "https://thehub.ba"
    
    article_path = "/artwork/31"
    
    check_robots(base, article_path)