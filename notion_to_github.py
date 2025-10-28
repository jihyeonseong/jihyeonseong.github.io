#!/usr/bin/env python3
"""
Notion to GitHub Blog Sync
Notion 데이터베이스의 글을 GitHub 블로그로 자동 동기화합니다.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any
import requests
from pathlib import Path


class NotionToGitHub:
    def __init__(self, notion_token: str, notion_database_id: str, github_token: str, 
                 github_repo: str, blog_posts_path: str = "_posts"):
        """
        Args:
            notion_token: Notion Integration Token
            notion_database_id: Notion Database ID
            github_token: GitHub Personal Access Token
            github_repo: GitHub 저장소 (예: "username/username.github.io")
            blog_posts_path: 블로그 포스트가 저장될 경로 (기본값: "_posts")
        """
        self.notion_token = notion_token
        self.notion_database_id = notion_database_id
        self.github_token = github_token
        self.github_repo = github_repo
        self.blog_posts_path = blog_posts_path
        
        self.notion_headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        self.github_headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_published_pages(self) -> List[Dict[str, Any]]:
        """Notion 데이터베이스에서 발행된(Published) 페이지 가져오기"""
        url = f"https://api.notion.com/v1/databases/{self.notion_database_id}/query"
        
        # Published 상태인 페이지만 필터링
        payload = {
            "filter": {
                "property": "Status",
                "status": {
                    "equals": "Published"
                }
            }
        }
        
        response = requests.post(url, headers=self.notion_headers, json=payload)
        response.raise_for_status()
        
        return response.json().get("results", [])
    
    def get_page_content(self, page_id: str) -> List[Dict[str, Any]]:
        """페이지의 블록 내용 가져오기"""
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        response = requests.get(url, headers=self.notion_headers)
        response.raise_for_status()
        
        return response.json().get("results", [])
    
    def extract_text_from_rich_text(self, rich_text: List[Dict]) -> str:
        """Rich text에서 일반 텍스트 추출"""
        if not rich_text:
            return ""
        return "".join([text.get("plain_text", "") for text in rich_text])
    
    def block_to_markdown(self, block: Dict[str, Any], level: int = 0) -> str:
        """Notion 블록을 마크다운으로 변환"""
        block_type = block.get("type")
        block_data = block.get(block_type, {})
        markdown = ""
        
        if block_type == "paragraph":
            text = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            markdown = f"{text}\n\n"
        
        elif block_type == "heading_1":
            text = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            markdown = f"# {text}\n\n"
        
        elif block_type == "heading_2":
            text = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            markdown = f"## {text}\n\n"
        
        elif block_type == "heading_3":
            text = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            markdown = f"### {text}\n\n"
        
        elif block_type == "bulleted_list_item":
            text = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            indent = "  " * level
            markdown = f"{indent}- {text}\n"
        
        elif block_type == "numbered_list_item":
            text = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            indent = "  " * level
            markdown = f"{indent}1. {text}\n"
        
        elif block_type == "code":
            code = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            language = block_data.get("language", "")
            markdown = f"```{language}\n{code}\n```\n\n"
        
        elif block_type == "quote":
            text = self.extract_text_from_rich_text(block_data.get("rich_text", []))
            markdown = f"> {text}\n\n"
        
        elif block_type == "divider":
            markdown = "---\n\n"
        
        elif block_type == "image":
            image_url = block_data.get("file", {}).get("url") or block_data.get("external", {}).get("url")
            caption = self.extract_text_from_rich_text(block_data.get("caption", []))
            markdown = f"![{caption}]({image_url})\n\n"
        
        return markdown
    
    def page_to_markdown(self, page: Dict[str, Any]) -> tuple[str, str, Dict[str, Any]]:
        """Notion 페이지를 마크다운으로 변환"""
        properties = page.get("properties", {})
        
        # 제목 추출
        title_prop = properties.get("Name") or properties.get("Title") or properties.get("제목")
        if title_prop:
            title = self.extract_text_from_rich_text(title_prop.get("title", []))
        else:
            title = "Untitled"
        
        # 날짜 추출
        date_prop = properties.get("Date") or properties.get("Created") or properties.get("날짜")
        if date_prop and date_prop.get("date"):
            date = date_prop["date"]["start"]
        else:
            date = page.get("created_time", "")[:10]
        
        # 태그 추출
        tags = []
        tags_prop = properties.get("Tags") or properties.get("태그")
        if tags_prop and tags_prop.get("multi_select"):
            tags = [tag["name"] for tag in tags_prop["multi_select"]]
        
        # 카테고리 추출
        category = ""
        category_prop = properties.get("Category") or properties.get("카테고리")
        if category_prop and category_prop.get("select"):
            category = category_prop["select"]["name"]
        
        # 페이지 내용 가져오기
        page_id = page["id"]
        blocks = self.get_page_content(page_id)
        
        # 블록을 마크다운으로 변환
        content = ""
        for block in blocks:
            content += self.block_to_markdown(block)
        
        # Front matter 생성
        front_matter = {
            "title": title,
            "date": date,
            "categories": [category] if category else [],
            "tags": tags
        }
        
        return title, content, front_matter
    
    def create_jekyll_post(self, title: str, content: str, front_matter: Dict[str, Any]) -> str:
        """Jekyll 형식의 포스트 생성"""
        # Front matter 작성
        yaml_front_matter = "---\n"
        yaml_front_matter += f"layout: post\n"
        yaml_front_matter += f"title: \"{front_matter['title']}\"\n"
        yaml_front_matter += f"date: {front_matter['date']}\n"
        
        if front_matter.get("categories"):
            yaml_front_matter += f"categories: {front_matter['categories']}\n"
        
        if front_matter.get("tags"):
            tags_str = " ".join(front_matter["tags"])
            yaml_front_matter += f"tags: [{tags_str}]\n"
        
        yaml_front_matter += "---\n\n"
        
        return yaml_front_matter + content
    
    def create_filename(self, date: str, title: str) -> str:
        """Jekyll 파일명 형식으로 변환 (YYYY-MM-DD-title.md)"""
        # 제목을 URL-safe하게 변환
        safe_title = re.sub(r'[^\w\s-]', '', title.lower())
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title.strip('-')
        
        return f"{date}-{safe_title}.md"
    
    def get_file_sha(self, filepath: str) -> str:
        """GitHub에서 파일의 SHA 가져오기 (업데이트를 위해 필요)"""
        url = f"https://api.github.com/repos/{self.github_repo}/contents/{filepath}"
        response = requests.get(url, headers=self.github_headers)
        
        if response.status_code == 200:
            return response.json().get("sha")
        return None
    
    def push_to_github(self, filepath: str, content: str, commit_message: str):
        """GitHub에 파일 푸시"""
        url = f"https://api.github.com/repos/{self.github_repo}/contents/{filepath}"
        
        # Base64 인코딩
        import base64
        content_encoded = base64.b64encode(content.encode()).decode()
        
        # 기존 파일이 있는지 확인
        sha = self.get_file_sha(filepath)
        
        payload = {
            "message": commit_message,
            "content": content_encoded,
            "branch": "main"  # 또는 "master"
        }
        
        if sha:
            payload["sha"] = sha
        
        response = requests.put(url, headers=self.github_headers, json=payload)
        response.raise_for_status()
        
        print(f"✓ {filepath} 업로드 완료")
    
    def sync(self):
        """Notion에서 GitHub 블로그로 동기화"""
        print("🔄 Notion에서 발행된 페이지 가져오는 중...")
        pages = self.get_published_pages()
        print(f"📄 {len(pages)}개의 발행된 페이지를 찾았습니다.")
        
        for i, page in enumerate(pages, 1):
            try:
                print(f"\n[{i}/{len(pages)}] 처리 중...")
                
                # 페이지를 마크다운으로 변환
                title, content, front_matter = self.page_to_markdown(page)
                print(f"  제목: {title}")
                
                # Jekyll 포스트 생성
                post_content = self.create_jekyll_post(title, content, front_matter)
                
                # 파일명 생성
                filename = self.create_filename(front_matter["date"], title)
                filepath = f"{self.blog_posts_path}/{filename}"
                
                # GitHub에 푸시
                commit_message = f"Post: {title}"
                self.push_to_github(filepath, post_content, commit_message)
                
            except Exception as e:
                print(f"  ✗ 오류 발생: {e}")
                continue
        
        print("\n✅ 동기화 완료!")


def main():
    # 환경 변수에서 설정 가져오기
    notion_token = os.getenv("NOTION_TOKEN")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO")
    blog_posts_path = os.getenv("BLOG_POSTS_PATH", "_posts")
    
    if not all([notion_token, notion_database_id, github_token, github_repo]):
        print("❌ 필수 환경 변수가 설정되지 않았습니다:")
        print("  - NOTION_TOKEN")
        print("  - NOTION_DATABASE_ID")
        print("  - GITHUB_TOKEN")
        print("  - GITHUB_REPO")
        return
    
    syncer = NotionToGitHub(
        notion_token=notion_token,
        notion_database_id=notion_database_id,
        github_token=github_token,
        github_repo=github_repo,
        blog_posts_path=blog_posts_path
    )
    
    syncer.sync()


if __name__ == "__main__":
    main()
