import csv

class BibleManager:
    def __init__(self, bible_path):
        self.bible_verses = {}
        with open(bible_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if len(row) >= 2:
                    self.bible_verses[row[0]] = f"{row[0]}: {row[1]}"

    def get_verse(self, verse_reference):
        # First, try for an exact match
        if verse_reference in self.bible_verses:
            return self.bible_verses[verse_reference]
        
        # If no exact match, find the closest match based on character overlap
        closest_match = max(self.bible_verses.keys(), 
                            key=lambda x: len(set(x) & set(verse_reference)))
        
        return self.bible_verses.get(closest_match, f"{verse_reference}: Verse not found.")
