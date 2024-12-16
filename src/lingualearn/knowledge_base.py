from typing import Dict, List, Optional, Tuple
import sqlite3
import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TranslationEntry:
    source_text: str
    target_text: str
    source_lang: str
    target_lang: str
    context: Optional[str] = None
    confidence_score: float = 0.0
    usage_count: int = 0
    last_used: datetime = datetime.now()

class KnowledgeBase:
    def __init__(self, db_path: str = 'translations.db'):
        """Initialize the knowledge base"""
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Create the necessary database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_text TEXT NOT NULL,
                    target_text TEXT NOT NULL,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    context TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_text, target_text, source_lang, target_lang)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contextual_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    rule_content TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    UNIQUE(source_lang, target_lang, rule_type, rule_content)
                )
            """)

    async def add_translation(self, entry: TranslationEntry) -> bool:
        """Add a new translation entry or update existing one"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO translations
                    (source_text, target_text, source_lang, target_lang, context,
                     confidence_score, usage_count, last_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.source_text,
                    entry.target_text,
                    entry.source_lang,
                    entry.target_lang,
                    entry.context,
                    entry.confidence_score,
                    entry.usage_count,
                    entry.last_used
                ))
                return True
        except Exception as e:
            print(f"Error adding translation: {e}")
            return False

    async def get_translation(self, 
                            source_text: str,
                            source_lang: str,
                            target_lang: str) -> Optional[TranslationEntry]:
        """Retrieve a translation if it exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM translations
                WHERE source_text = ? 
                AND source_lang = ? 
                AND target_lang = ?
                ORDER BY confidence_score DESC
                LIMIT 1
            """, (source_text, source_lang, target_lang))
            
            row = cursor.fetchone()
            if row:
                return TranslationEntry(
                    source_text=row[1],
                    target_text=row[2],
                    source_lang=row[3],
                    target_lang=row[4],
                    context=row[5],
                    confidence_score=row[6],
                    usage_count=row[7],
                    last_used=datetime.fromisoformat(row[8])
                )
        return None

    async def learn_contextual_rule(self,
                                  source_lang: str,
                                  target_lang: str,
                                  rule_type: str,
                                  rule_content: Dict) -> None:
        """Learn a new translation rule from context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO contextual_rules
                    (source_lang, target_lang, rule_type, rule_content)
                    VALUES (?, ?, ?, ?)
                """, (
                    source_lang,
                    target_lang,
                    rule_type,
                    json.dumps(rule_content)
                ))
        except Exception as e:
            print(f"Error learning rule: {e}")

    async def get_contextual_rules(self,
                                 source_lang: str,
                                 target_lang: str,
                                 min_confidence: float = 0.5
                                 ) -> List[Dict]:
        """Get learned translation rules for a language pair"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT rule_type, rule_content, confidence_score
                FROM contextual_rules
                WHERE source_lang = ?
                AND target_lang = ?
                AND confidence_score >= ?
            """, (source_lang, target_lang, min_confidence))
            
            return [{
                'type': row[0],
                'content': json.loads(row[1]),
                'confidence': row[2]
            } for row in cursor.fetchall()]

    async def update_confidence(self,
                              source_text: str,
                              target_text: str,
                              source_lang: str,
                              target_lang: str,
                              success: bool) -> None:
        """Update confidence score based on translation success"""
        with sqlite3.connect(self.db_path) as conn:
            # Increase or decrease confidence based on success
            delta = 0.1 if success else -0.1
            conn.execute("""
                UPDATE translations
                SET confidence_score = ROUND(CASE
                    WHEN confidence_score + ? > 1.0 THEN 1.0
                    WHEN confidence_score + ? < 0.0 THEN 0.0
                    ELSE confidence_score + ?
                    END, 2),
                    usage_count = usage_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE source_text = ?
                AND target_text = ?
                AND source_lang = ?
                AND target_lang = ?
            """, (delta, delta, delta, source_text, target_text, source_lang, target_lang))