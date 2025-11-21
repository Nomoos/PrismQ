# WordPress Implementation Manual: Custom Post Type + TranslatePress + API

**For NomStory Project - 26 Language Story Publishing Platform**

**Date:** November 2024  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: WordPress Installation & Setup](#phase-1-wordpress-installation--setup)
4. [Phase 2: Custom Post Type Implementation](#phase-2-custom-post-type-implementation)
5. [Phase 3: TranslatePress Setup](#phase-3-translatepress-setup)
6. [Phase 4: REST API Configuration](#phase-4-rest-api-configuration)
7. [Phase 5: Publishing Stories via API](#phase-5-publishing-stories-via-api)
8. [Phase 6: Automated Workflow](#phase-6-automated-workflow)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Overview

This manual guides you through implementing a WordPress-based multilingual story publishing platform with:
- Custom Post Type for stories
- TranslatePress for 26 language translations
- REST API for programmatic publishing
- Automated workflow for story creation and translation

**Estimated Setup Time:** 2-3 hours  
**Technical Level:** Intermediate  
**Cost:** $329-929 first year, $400-700/year ongoing

---

## Prerequisites

### Required:
- Domain name (e.g., nomstory.com) - $10-15/year
- WordPress hosting (recommended: Cloudways, SiteGround, or WP Engine) - $15-50/month
- TranslatePress Personal license - $89/year
- DeepL API account - $5-20/month
- Basic understanding of WordPress, PHP, and REST APIs

### Optional:
- Git for version control
- Python or Node.js for automation scripts
- Code editor (VS Code, Sublime Text)

---

## Phase 1: WordPress Installation & Setup

### Step 1.1: Install WordPress

**Via Hosting Control Panel:**
```bash
1. Log in to your hosting control panel
2. Find "WordPress Installer" or "Softaculous"
3. Click "Install WordPress"
4. Fill in details:
   - Domain: nomstory.com
   - Site Title: Nom Story
   - Admin Username: (secure username)
   - Admin Password: (strong password)
   - Admin Email: your@email.com
5. Click "Install"
```

**Manual Installation:**
```bash
# Download WordPress
wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz

# Upload to server via FTP/SSH
# Create database in hosting panel
# Run installation at: https://nomstory.com/wp-admin/install.php
```

**Time:** 10-15 minutes

### Step 1.2: Basic WordPress Configuration

1. **Go to Settings → General:**
   - Site Title: Nom Story
   - Tagline: Short Stories in 26 Languages
   - WordPress Address: https://nomstory.com
   - Site Address: https://nomstory.com
   - Timezone: Your timezone
   - Date/Time Format: Set preferences

2. **Go to Settings → Permalinks:**
   - Select: "Post name" (for SEO-friendly URLs)
   - Custom Structure: `/%postname%/`

3. **Install Essential Plugins:**
   ```
   - Wordfence Security (free) - for security
   - WP Rocket ($49/year) - for caching/performance (optional but recommended)
   - Advanced Custom Fields (ACF) (free/$49/year) - for custom metadata
   ```

**Time:** 15-20 minutes

---

## Phase 2: Custom Post Type Implementation

### Step 2.1: Create Custom Post Type Plugin

**Option A: Using Plugin (Easier)**

1. Install "Custom Post Type UI" plugin:
   ```
   WordPress Admin → Plugins → Add New → Search "Custom Post Type UI" → Install → Activate
   ```

2. Configure Story Post Type:
   ```
   CPT UI → Add/Edit Post Types
   
   Basic Settings:
   - Post Type Slug: story
   - Plural Label: Stories
   - Singular Label: Story
   
   Additional Labels:
   - Add New: Add New Story
   - Add New Item: Add New Story
   - Edit Item: Edit Story
   - All Items: All Stories
   
   Settings:
   - Public: True
   - Show in REST API: True (CRITICAL for API access)
   - REST API Base Slug: stories
   - Has Archive: True
   - Hierarchical: False
   - Supports: Title, Editor, Featured Image, Revisions, Custom Fields
   
   Save Post Type
   ```

**Option B: Code Implementation (More Control)**

Create plugin file: `/wp-content/plugins/nomstory-custom-post-types/nomstory-cpt.php`

```php
<?php
/**
 * Plugin Name: NomStory Custom Post Types
 * Description: Custom post types for NomStory project
 * Version: 1.0
 * Author: Your Name
 */

// Register Story Custom Post Type
function nomstory_register_story_post_type() {
    $labels = array(
        'name'                  => 'Stories',
        'singular_name'         => 'Story',
        'menu_name'             => 'Stories',
        'add_new'               => 'Add New Story',
        'add_new_item'          => 'Add New Story',
        'edit_item'             => 'Edit Story',
        'new_item'              => 'New Story',
        'view_item'             => 'View Story',
        'search_items'          => 'Search Stories',
        'not_found'             => 'No stories found',
        'not_found_in_trash'    => 'No stories found in trash',
        'all_items'             => 'All Stories',
    );

    $args = array(
        'labels'                => $labels,
        'public'                => true,
        'publicly_queryable'    => true,
        'show_ui'               => true,
        'show_in_menu'          => true,
        'show_in_rest'          => true, // CRITICAL: Enables REST API
        'rest_base'             => 'stories',
        'rest_controller_class' => 'WP_REST_Posts_Controller',
        'query_var'             => true,
        'rewrite'               => array( 'slug' => 'story' ),
        'capability_type'       => 'post',
        'has_archive'           => true,
        'hierarchical'          => false,
        'menu_position'         => 5,
        'menu_icon'             => 'dashicons-book-alt',
        'supports'              => array(
            'title',
            'editor',
            'thumbnail',
            'excerpt',
            'revisions',
            'custom-fields',
            'author'
        ),
        'taxonomies'            => array( 'category', 'post_tag' ),
    );

    register_post_type( 'story', $args );
}
add_action( 'init', 'nomstory_register_story_post_type' );

// Register Custom Taxonomies (Categories for Stories)
function nomstory_register_story_taxonomies() {
    // Story Type Taxonomy
    register_taxonomy(
        'story_type',
        'story',
        array(
            'label'         => 'Story Types',
            'hierarchical'  => true,
            'show_in_rest'  => true,
            'rest_base'     => 'story-types',
            'rewrite'       => array( 'slug' => 'story-type' ),
        )
    );

    // Age Rating Taxonomy
    register_taxonomy(
        'age_rating',
        'story',
        array(
            'label'         => 'Age Ratings',
            'hierarchical'  => true,
            'show_in_rest'  => true,
            'rest_base'     => 'age-ratings',
            'rewrite'       => array( 'slug' => 'age-rating' ),
        )
    );
}
add_action( 'init', 'nomstory_register_story_taxonomies' );

// Add Custom Columns to Stories List
function nomstory_story_columns( $columns ) {
    $columns['story_type'] = 'Type';
    $columns['age_rating'] = 'Age Rating';
    $columns['reading_time'] = 'Reading Time';
    return $columns;
}
add_filter( 'manage_story_posts_columns', 'nomstory_story_columns' );

// Populate Custom Columns
function nomstory_story_column_content( $column, $post_id ) {
    switch ( $column ) {
        case 'story_type':
            $terms = get_the_terms( $post_id, 'story_type' );
            if ( $terms && ! is_wp_error( $terms ) ) {
                echo esc_html( $terms[0]->name );
            } else {
                echo '—';
            }
            break;
        case 'age_rating':
            $terms = get_the_terms( $post_id, 'age_rating' );
            if ( $terms && ! is_wp_error( $terms ) ) {
                echo esc_html( $terms[0]->name );
            } else {
                echo '—';
            }
            break;
        case 'reading_time':
            $time = get_post_meta( $post_id, 'reading_time', true );
            echo $time ? esc_html( $time ) . ' min' : '—';
            break;
    }
}
add_action( 'manage_story_posts_custom_column', 'nomstory_story_column_content', 10, 2 );
?>
```

3. **Activate the Plugin:**
   ```
   WordPress Admin → Plugins → Installed Plugins → Find "NomStory Custom Post Types" → Activate
   ```

4. **Verify Installation:**
   - Check WordPress Admin sidebar for "Stories" menu item
   - Visit: https://nomstory.com/wp-json/wp/v2/stories (should return JSON)

**Time:** 20-30 minutes

### Step 2.2: Add Custom Fields with ACF

1. **Install Advanced Custom Fields (ACF):**
   ```
   Plugins → Add New → Search "Advanced Custom Fields" → Install → Activate
   ```

2. **Create Field Group for Stories:**
   ```
   ACF → Field Groups → Add New
   
   Title: Story Metadata
   
   Add Fields:
   
   Field 1:
   - Field Label: Story Type
   - Field Name: story_type_meta
   - Field Type: Select
   - Choices:
     scary : Scary Story
     family_drama : Family Drama
     short_story : Short Story
     romance : Romance
     mystery : Mystery
   
   Field 2:
   - Field Label: Age Rating
   - Field Name: age_rating
   - Field Type: Select
   - Choices:
     10-15 : Ages 10-15
     15-20 : Ages 15-20
     20-25 : Ages 20-25
     all_ages : All Ages
   
   Field 3:
   - Field Label: Reading Time (minutes)
   - Field Name: reading_time
   - Field Type: Number
   - Min: 1
   - Max: 60
   
   Field 4:
   - Field Label: YouTube Video URL
   - Field Name: youtube_url
   - Field Type: URL
   
   Field 5:
   - Field Label: TikTok Video URL
   - Field Name: tiktok_url
   - Field Type: URL
   
   Field 6:
   - Field Label: Instagram Reel URL
   - Field Name: instagram_url
   - Field Type: URL
   
   Field 7:
   - Field Label: Publication Status
   - Field Name: publication_status
   - Field Type: Select
   - Choices:
     draft : Draft
     scheduled : Scheduled
     published : Published
     archived : Archived
   
   Location Rules:
   - Show this field group if: Post Type is equal to story
   
   Settings:
   - Show in REST API: Yes (CRITICAL)
   
   Save Field Group
   ```

**Time:** 15-20 minutes

---

## Phase 3: TranslatePress Setup

### Step 3.1: Install TranslatePress

1. **Purchase License:**
   - Go to: https://translatepress.com/
   - Buy "TranslatePress Personal" - $89/year
   - Download plugin ZIP file

2. **Install Plugin:**
   ```
   WordPress Admin → Plugins → Add New → Upload Plugin → Choose File
   → Select translatepress-personal.zip → Install Now → Activate
   ```

3. **Enter License Key:**
   ```
   Settings → TranslatePress → License
   → Enter your license key → Activate License
   ```

**Time:** 5 minutes

### Step 3.2: Configure Languages

1. **Go to Settings → TranslatePress → General:**
   ```
   Default Language: English
   
   Add Languages (click "+Add"):
   - Czech (cs)
   - German (de)
   - Spanish (es)
   - Portuguese (Brazil) (pt-BR)
   - French (fr)
   - Hindi (hi)
   - Turkish (tr)
   - Indonesian (id)
   - Vietnamese (vi)
   - Filipino (fil)
   - Japanese (ja)
   - Korean (ko)
   - Polish (pl)
   - Dutch (nl)
   - Ukrainian (uk)
   - Romanian (ro)
   - Hungarian (hu)
   - Swedish (sv)
   - Chinese (Simplified) (zh-CN)
   - Arabic (ar)
   - Bengali (bn)
   - Tamil (ta)
   - Urdu (ur)
   - Thai (th)
   - Italian (it)
   
   URL Structure: Subdirectory (example.com/en/...)
   
   Use a language switcher: Yes
   Shortcode: Yes
   Floater: Yes (shows flag switcher)
   
   Native language names: Yes
   Language Switcher: Flags with Language Name
   ```

2. **Go to Settings → TranslatePress → Automatic Translation:**
   ```
   Enable Automatic Translation: Yes
   
   Translation Engine: DeepL API (Recommended)
   - Get API key from: https://www.deepl.com/pro-api
   - Free tier: 500,000 characters/month
   - Paid tier: $5.49/month + $0.00002/character
   
   Enter DeepL API Key: [your-api-key]
   
   Test API: Click "Test API Key" (should show green checkmark)
   
   Save Settings
   ```

**Alternative: Google Translate API:**
```
Translation Engine: Google Translate v2
- Get API key from: Google Cloud Console
- Pricing: $20 per 1M characters
- Less accurate than DeepL but cheaper for high volume
```

**Time:** 20-30 minutes

### Step 3.3: Configure Language Switcher

1. **Add Language Switcher to Navigation:**
   ```
   Appearance → Menus
   → Select your main menu
   → Check "Language Switcher" in left sidebar
   → Add to Menu
   → Drag to desired position (usually top-right)
   → Save Menu
   ```

2. **Customize Switcher Appearance:**
   ```
   Settings → TranslatePress → General → Advanced Settings
   
   Language Switcher Settings:
   - Flags: Show
   - Language Names: Show (Full)
   - Display as: Dropdown
   - Position: Top Right
   
   CSS Customization (optional):
   Appearance → Customize → Additional CSS
   ```

   ```css
   /* Style language switcher like Wikipedia */
   .trp-language-switcher-container {
       position: absolute;
       top: 20px;
       right: 20px;
       z-index: 1000;
   }
   
   .trp-ls-shortcode-language {
       display: inline-block;
       margin: 0 5px;
   }
   
   .trp-ls-shortcode-language a {
       padding: 5px 10px;
       border: 1px solid #ccc;
       border-radius: 3px;
       text-decoration: none;
       transition: background-color 0.3s;
   }
   
   .trp-ls-shortcode-language a:hover {
       background-color: #f0f0f0;
   }
   
   .trp-ls-shortcode-current-language {
       font-weight: bold;
       background-color: #e8f4f8;
   }
   ```

**Time:** 10-15 minutes

### Step 3.4: Test Translation

1. **Create Test Story:**
   ```
   Stories → Add New Story
   
   Title: The Haunted House
   Content: Once upon a time, in a small village, there was an old haunted house...
   
   Publish
   ```

2. **Translate Story:**
   ```
   Method 1: Manual Translation
   - View the story on frontend
   - Click "Translate Page" in bottom-left corner (TranslatePress editor)
   - Select target language from dropdown (e.g., Czech)
   - Click text to translate manually
   - Save translation
   
   Method 2: Automatic Translation
   - Click "Translate Entire Page Automatically"
   - Select DeepL or Google Translate
   - Click "Translate"
   - Review and edit translations
   - Save
   ```

3. **Verify Translation:**
   - Switch language using flag switcher
   - Check URL structure: `/cs/story/the-haunted-house/`
   - Verify content is translated

**Time:** 10-15 minutes

---

## Phase 4: REST API Configuration

### Step 4.1: Enable REST API

**REST API is enabled by default in WordPress 4.7+**, but verify:

1. **Test API Access:**
   ```bash
   # Test general API
   curl https://nomstory.com/wp-json/
   
   # Test stories endpoint
   curl https://nomstory.com/wp-json/wp/v2/stories
   
   # Should return JSON with stories list
   ```

2. **Verify Custom Post Type in API:**
   ```bash
   # Should show story post type
   curl https://nomstory.com/wp-json/wp/v2/types/story
   ```

**Time:** 5 minutes

### Step 4.2: Set Up Authentication

**Method 1: Application Passwords (Recommended - Built-in WordPress 5.6+)**

1. **Create Application Password:**
   ```
   WordPress Admin → Users → Profile
   → Scroll to "Application Passwords" section
   → Application Name: "Story Publishing Script"
   → Click "Add New Application Password"
   → SAVE THE PASSWORD (shown only once): xxxx xxxx xxxx xxxx xxxx xxxx
   ```

2. **Test Authentication:**
   ```bash
   # Test with curl
   curl -X GET https://nomstory.com/wp-json/wp/v2/stories \
     -u "username:xxxx xxxx xxxx xxxx xxxx xxxx"
   
   # Should return 200 OK with stories data
   ```

**Method 2: JWT Authentication (Alternative)**

1. **Install JWT Plugin:**
   ```
   # Download JWT Authentication plugin
   # https://github.com/Tmeister/wp-api-jwt-auth
   
   Upload and activate plugin
   ```

2. **Configure JWT:**
   Add to `wp-config.php`:
   ```php
   define('JWT_AUTH_SECRET_KEY', 'your-secret-key-here');
   define('JWT_AUTH_CORS_ENABLE', true);
   ```

3. **Get JWT Token:**
   ```bash
   curl -X POST https://nomstory.com/wp-json/jwt-auth/v1/token \
     -H "Content-Type: application/json" \
     -d '{"username":"your-username","password":"your-password"}'
   
   # Returns: {"token":"eyJ0eXAiOiJKV1QiLCJhbGc..."}
   ```

**Time:** 10-15 minutes

### Step 4.3: Test API Endpoints

**Available Endpoints:**

```bash
# 1. List all stories
GET /wp-json/wp/v2/stories

# 2. Get single story
GET /wp-json/wp/v2/stories/{id}

# 3. Get story revisions
GET /wp-json/wp/v2/stories/{id}/revisions

# 4. Create story
POST /wp-json/wp/v2/stories

# 5. Update story
POST /wp-json/wp/v2/stories/{id}

# 6. Delete story
DELETE /wp-json/wp/v2/stories/{id}

# 7. Get story types (taxonomy)
GET /wp-json/wp/v2/story-types

# 8. Get translations (TranslatePress)
GET /wp-json/translatepress/v1/translations?language=cs

# 9. Get ACF fields
GET /wp-json/acf/v3/stories/{id}
```

**Test Examples:**

```bash
# List stories
curl https://nomstory.com/wp-json/wp/v2/stories

# Get specific story
curl https://nomstory.com/wp-json/wp/v2/stories/123

# Create story (requires authentication)
curl -X POST https://nomstory.com/wp-json/wp/v2/stories \
  -u "username:app-password" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Story",
    "content": "Story content here",
    "status": "publish"
  }'
```

**Time:** 10 minutes

---

## Phase 5: Publishing Stories via API

### Step 5.1: Python Publishing Script

Create file: `publish_story.py`

```python
#!/usr/bin/env python3
"""
NomStory WordPress Publishing Script
Publishes stories to WordPress with automatic translation
"""

import requests
import json
import time
from typing import Dict, List, Optional

class NomStoryPublisher:
    def __init__(self, wp_url: str, username: str, app_password: str):
        """
        Initialize publisher
        
        Args:
            wp_url: WordPress site URL (e.g., https://nomstory.com)
            username: WordPress username
            app_password: Application password from WordPress
        """
        self.wp_url = wp_url.rstrip('/')
        self.auth = (username, app_password)
        self.api_base = f"{self.wp_url}/wp-json/wp/v2"
        
    def create_story(
        self,
        title: str,
        content: str,
        story_type: str = "short_story",
        age_rating: str = "15-20",
        reading_time: int = 5,
        youtube_url: Optional[str] = None,
        tiktok_url: Optional[str] = None,
        instagram_url: Optional[str] = None,
        status: str = "publish",
        featured_image_id: Optional[int] = None
    ) -> Dict:
        """
        Create and publish a story
        
        Args:
            title: Story title
            content: Story content (HTML allowed)
            story_type: Type of story (scary, family_drama, short_story, etc.)
            age_rating: Target age rating (10-15, 15-20, 20-25, all_ages)
            reading_time: Estimated reading time in minutes
            youtube_url: URL to YouTube video
            tiktok_url: URL to TikTok video
            instagram_url: URL to Instagram reel
            status: Post status (draft, publish, pending, private)
            featured_image_id: WordPress media ID for featured image
            
        Returns:
            Dictionary with created story data including ID
        """
        
        # Prepare story data
        story_data = {
            "title": title,
            "content": content,
            "status": status,
            "meta": {
                "story_type_meta": story_type,
                "age_rating": age_rating,
                "reading_time": reading_time,
            }
        }
        
        # Add optional fields
        if youtube_url:
            story_data["meta"]["youtube_url"] = youtube_url
        if tiktok_url:
            story_data["meta"]["tiktok_url"] = tiktok_url
        if instagram_url:
            story_data["meta"]["instagram_url"] = instagram_url
        if featured_image_id:
            story_data["featured_media"] = featured_image_id
            
        # Make API request
        response = requests.post(
            f"{self.api_base}/stories",
            auth=self.auth,
            json=story_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print(f"✅ Story created successfully: {title}")
            return response.json()
        else:
            print(f"❌ Error creating story: {response.status_code}")
            print(response.text)
            return None
    
    def translate_story(self, story_id: int, languages: List[str] = None) -> Dict:
        """
        Trigger automatic translation for a story
        
        Args:
            story_id: WordPress post ID
            languages: List of language codes to translate to
                      If None, translates to all configured languages
            
        Returns:
            Translation status
        """
        
        if languages is None:
            # Default to all NomStory languages
            languages = [
                'cs', 'de', 'es', 'pt-BR', 'fr', 'hi', 'tr', 'id', 'vi',
                'fil', 'ja', 'ko', 'pl', 'nl', 'uk', 'ro', 'hu', 'sv',
                'zh-CN', 'ar', 'bn', 'ta', 'ur', 'th', 'it'
            ]
        
        print(f"🌍 Translating story {story_id} to {len(languages)} languages...")
        
        # Get story URL
        story_response = requests.get(
            f"{self.api_base}/stories/{story_id}",
            auth=self.auth
        )
        
        if story_response.status_code != 200:
            print(f"❌ Error fetching story: {story_response.status_code}")
            return None
            
        story_url = story_response.json().get('link')
        
        # Trigger automatic translation
        # Note: TranslatePress translates on-demand when page is visited
        # We'll visit each language version to trigger translation
        
        translated_count = 0
        for lang in languages:
            # Build language-specific URL
            lang_url = story_url.replace(self.wp_url, f"{self.wp_url}/{lang}")
            
            # Visit URL to trigger translation
            try:
                response = requests.get(lang_url, timeout=10)
                if response.status_code == 200:
                    translated_count += 1
                    print(f"  ✓ {lang}: Translated")
                else:
                    print(f"  ✗ {lang}: Error ({response.status_code})")
                    
                # Small delay to avoid overwhelming server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ✗ {lang}: Exception ({str(e)})")
        
        print(f"✅ Translation complete: {translated_count}/{len(languages)} languages")
        
        return {
            "story_id": story_id,
            "total_languages": len(languages),
            "translated": translated_count
        }
    
    def update_story(self, story_id: int, updates: Dict) -> Dict:
        """
        Update an existing story
        
        Args:
            story_id: WordPress post ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated story data
        """
        
        response = requests.post(
            f"{self.api_base}/stories/{story_id}",
            auth=self.auth,
            json=updates,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ Story {story_id} updated successfully")
            return response.json()
        else:
            print(f"❌ Error updating story: {response.status_code}")
            print(response.text)
            return None
    
    def get_story(self, story_id: int) -> Dict:
        """Get story by ID"""
        response = requests.get(
            f"{self.api_base}/stories/{story_id}",
            auth=self.auth
        )
        return response.json() if response.status_code == 200 else None
    
    def list_stories(self, per_page: int = 10, page: int = 1) -> List[Dict]:
        """List stories with pagination"""
        response = requests.get(
            f"{self.api_base}/stories",
            auth=self.auth,
            params={"per_page": per_page, "page": page}
        )
        return response.json() if response.status_code == 200 else []
    
    def delete_story(self, story_id: int) -> bool:
        """Delete a story"""
        response = requests.delete(
            f"{self.api_base}/stories/{story_id}",
            auth=self.auth
        )
        return response.status_code == 200


# Example usage
if __name__ == "__main__":
    # Initialize publisher
    publisher = NomStoryPublisher(
        wp_url="https://nomstory.com",
        username="your-username",
        app_password="xxxx xxxx xxxx xxxx xxxx xxxx"
    )
    
    # Create a story
    story = publisher.create_story(
        title="The Haunted Mansion",
        content="""
        <p>On a dark and stormy night, Sarah found herself standing before 
        the old Blackwood Mansion. The locals had warned her to stay away, 
        but curiosity got the better of her.</p>
        
        <p>As she pushed open the creaking door, a chill ran down her spine. 
        Inside, shadows danced in the candlelight, and she could hear 
        whispers echoing through the empty halls.</p>
        
        <p>"Hello?" she called out. "Is anyone there?"</p>
        
        <p>The only response was the sound of footsteps approaching from 
        the darkness above...</p>
        """,
        story_type="scary",
        age_rating="15-20",
        reading_time=3,
        status="publish"
    )
    
    if story:
        story_id = story['id']
        print(f"\n📚 Story ID: {story_id}")
        print(f"🔗 URL: {story['link']}")
        
        # Translate to all languages
        publisher.translate_story(story_id)
        
        print(f"\n✅ Story published and translated successfully!")
        print(f"View at: {story['link']}")
```

**Save and make executable:**
```bash
chmod +x publish_story.py
```

**Time:** 30 minutes to set up

### Step 5.2: Node.js Publishing Script (Alternative)

Create file: `publish_story.js`

```javascript
#!/usr/bin/env node
/**
 * NomStory WordPress Publishing Script (Node.js)
 * Publishes stories to WordPress with automatic translation
 */

const axios = require('axios');

class NomStoryPublisher {
    constructor(wpUrl, username, appPassword) {
        this.wpUrl = wpUrl.replace(/\/$/, '');
        this.auth = {
            username: username,
            password: appPassword
        };
        this.apiBase = `${this.wpUrl}/wp-json/wp/v2`;
    }

    async createStory({
        title,
        content,
        storyType = 'short_story',
        ageRating = '15-20',
        readingTime = 5,
        youtubeUrl = null,
        tiktokUrl = null,
        instagramUrl = null,
        status = 'publish',
        featuredImageId = null
    }) {
        try {
            const storyData = {
                title: title,
                content: content,
                status: status,
                meta: {
                    story_type_meta: storyType,
                    age_rating: ageRating,
                    reading_time: readingTime
                }
            };

            if (youtubeUrl) storyData.meta.youtube_url = youtubeUrl;
            if (tiktokUrl) storyData.meta.tiktok_url = tiktokUrl;
            if (instagramUrl) storyData.meta.instagram_url = instagramUrl;
            if (featuredImageId) storyData.featured_media = featuredImageId;

            const response = await axios.post(
                `${this.apiBase}/stories`,
                storyData,
                { auth: this.auth }
            );

            console.log(`✅ Story created successfully: ${title}`);
            return response.data;

        } catch (error) {
            console.error(`❌ Error creating story: ${error.message}`);
            if (error.response) {
                console.error(error.response.data);
            }
            return null;
        }
    }

    async translateStory(storyId, languages = null) {
        if (!languages) {
            languages = [
                'cs', 'de', 'es', 'pt-BR', 'fr', 'hi', 'tr', 'id', 'vi',
                'fil', 'ja', 'ko', 'pl', 'nl', 'uk', 'ro', 'hu', 'sv',
                'zh-CN', 'ar', 'bn', 'ta', 'ur', 'th', 'it'
            ];
        }

        console.log(`🌍 Translating story ${storyId} to ${languages.length} languages...`);

        try {
            const storyResponse = await axios.get(
                `${this.apiBase}/stories/${storyId}`,
                { auth: this.auth }
            );

            const storyUrl = storyResponse.data.link;
            let translatedCount = 0;

            for (const lang of languages) {
                const langUrl = storyUrl.replace(this.wpUrl, `${this.wpUrl}/${lang}`);

                try {
                    const response = await axios.get(langUrl, { timeout: 10000 });
                    if (response.status === 200) {
                        translatedCount++;
                        console.log(`  ✓ ${lang}: Translated`);
                    }
                } catch (error) {
                    console.log(`  ✗ ${lang}: Error`);
                }

                await new Promise(resolve => setTimeout(resolve, 500));
            }

            console.log(`✅ Translation complete: ${translatedCount}/${languages.length} languages`);

            return {
                storyId: storyId,
                totalLanguages: languages.length,
                translated: translatedCount
            };

        } catch (error) {
            console.error(`❌ Error translating story: ${error.message}`);
            return null;
        }
    }

    async updateStory(storyId, updates) {
        try {
            const response = await axios.post(
                `${this.apiBase}/stories/${storyId}`,
                updates,
                { auth: this.auth }
            );

            console.log(`✅ Story ${storyId} updated successfully`);
            return response.data;

        } catch (error) {
            console.error(`❌ Error updating story: ${error.message}`);
            return null;
        }
    }

    async getStory(storyId) {
        try {
            const response = await axios.get(
                `${this.apiBase}/stories/${storyId}`,
                { auth: this.auth }
            );
            return response.data;
        } catch (error) {
            console.error(`❌ Error getting story: ${error.message}`);
            return null;
        }
    }

    async listStories(perPage = 10, page = 1) {
        try {
            const response = await axios.get(
                `${this.apiBase}/stories`,
                {
                    auth: this.auth,
                    params: { per_page: perPage, page: page }
                }
            );
            return response.data;
        } catch (error) {
            console.error(`❌ Error listing stories: ${error.message}`);
            return [];
        }
    }

    async deleteStory(storyId) {
        try {
            await axios.delete(
                `${this.apiBase}/stories/${storyId}`,
                { auth: this.auth }
            );
            console.log(`✅ Story ${storyId} deleted successfully`);
            return true;
        } catch (error) {
            console.error(`❌ Error deleting story: ${error.message}`);
            return false;
        }
    }
}

// Example usage
async function main() {
    const publisher = new NomStoryPublisher(
        'https://nomstory.com',
        'your-username',
        'xxxx xxxx xxxx xxxx xxxx xxxx'
    );

    const story = await publisher.createStory({
        title: 'The Haunted Mansion',
        content: `
            <p>On a dark and stormy night, Sarah found herself standing before 
            the old Blackwood Mansion. The locals had warned her to stay away, 
            but curiosity got the better of her.</p>
            
            <p>As she pushed open the creaking door, a chill ran down her spine. 
            Inside, shadows danced in the candlelight, and she could hear 
            whispers echoing through the empty halls.</p>
            
            <p>"Hello?" she called out. "Is anyone there?"</p>
            
            <p>The only response was the sound of footsteps approaching from 
            the darkness above...</p>
        `,
        storyType: 'scary',
        ageRating: '15-20',
        readingTime: 3,
        status: 'publish'
    });

    if (story) {
        console.log(`\n📚 Story ID: ${story.id}`);
        console.log(`🔗 URL: ${story.link}`);

        await publisher.translateStory(story.id);

        console.log(`\n✅ Story published and translated successfully!`);
        console.log(`View at: ${story.link}`);
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = NomStoryPublisher;
```

**Install dependencies and run:**
```bash
npm install axios
chmod +x publish_story.js
node publish_story.js
```

**Time:** 30 minutes to set up

---

## Phase 6: Automated Workflow

### Step 6.1: Complete Publishing Workflow

Create file: `workflow.py`

```python
#!/usr/bin/env python3
"""
Complete NomStory Publishing Workflow
Handles story creation, translation, and video embedding
"""

import os
import time
from publish_story import NomStoryPublisher

# Configuration
WP_URL = os.getenv('WP_URL', 'https://nomstory.com')
WP_USERNAME = os.getenv('WP_USERNAME', 'your-username')
WP_APP_PASSWORD = os.getenv('WP_APP_PASSWORD', 'xxxx xxxx xxxx xxxx xxxx xxxx')

def publish_complete_story(
    title: str,
    content: str,
    story_type: str = "scary",
    age_rating: str = "15-20",
    reading_time: int = 5,
    youtube_url: str = None,
    tiktok_url: str = None,
    instagram_url: str = None
):
    """
    Complete workflow to publish a story with translations
    
    Steps:
    1. Create story in WordPress
    2. Trigger automatic translations (26 languages)
    3. Add video URLs
    4. Publish to all platforms
    """
    
    print("=" * 60)
    print("NomStory Publishing Workflow")
    print("=" * 60)
    
    # Initialize publisher
    publisher = NomStoryPublisher(WP_URL, WP_USERNAME, WP_APP_PASSWORD)
    
    # Step 1: Create story
    print("\n📝 Step 1: Creating story...")
    story = publisher.create_story(
        title=title,
        content=content,
        story_type=story_type,
        age_rating=age_rating,
        reading_time=reading_time,
        youtube_url=youtube_url,
        tiktok_url=tiktok_url,
        instagram_url=instagram_url,
        status="publish"
    )
    
    if not story:
        print("❌ Failed to create story. Aborting.")
        return None
    
    story_id = story['id']
    print(f"✅ Story created with ID: {story_id}")
    print(f"🔗 English URL: {story['link']}")
    
    # Step 2: Translate story
    print("\n🌍 Step 2: Translating story to 26 languages...")
    print("This may take 2-3 minutes...")
    
    translation_result = publisher.translate_story(story_id)
    
    if translation_result:
        print(f"✅ Translated to {translation_result['translated']} languages")
    
    # Step 3: Summary
    print("\n" + "=" * 60)
    print("✅ PUBLISHING COMPLETE!")
    print("=" * 60)
    print(f"📚 Story: {title}")
    print(f"🆔 ID: {story_id}")
    print(f"🔗 URL: {story['link']}")
    print(f"🌍 Languages: 26 (English + 25 translations)")
    print(f"⏱️  Reading Time: {reading_time} minutes")
    print(f"🎯 Target Age: {age_rating}")
    print(f"📁 Type: {story_type}")
    
    if youtube_url:
        print(f"🎥 YouTube: {youtube_url}")
    if tiktok_url:
        print(f"📱 TikTok: {tiktok_url}")
    if instagram_url:
        print(f"📷 Instagram: {instagram_url}")
    
    print("\n💡 Next steps:")
    print("  1. Review story at: " + story['link'])
    print("  2. Check translations by switching language flags")
    print("  3. Share on social media")
    print("  4. Monitor analytics")
    
    return story

# Example: Publish a scary story
if __name__ == "__main__":
    story = publish_complete_story(
        title="The Midnight Visitor",
        content="""
        <h2>Chapter 1: The Knock</h2>
        
        <p>It was exactly midnight when I heard the knock at my door. 
        I lived alone in a remote cabin, miles from the nearest town. 
        No one should have been out there at this hour.</p>
        
        <p>*Knock, knock, knock.*</p>
        
        <p>Three deliberate raps, each one louder than the last. 
        I froze in my chair, my book falling from my trembling hands.</p>
        
        <h2>Chapter 2: The Voice</h2>
        
        <p>"Let me in," a voice whispered through the door. "It's cold out here."</p>
        
        <p>But something about that voice made my blood run cold. It sounded 
        wrong—hollow, echoing, as if coming from somewhere far away.</p>
        
        <p>"Who's there?" I called out, trying to keep my voice steady.</p>
        
        <p>"You know who I am," the voice replied. "You've always known."</p>
        
        <h2>Chapter 3: The Truth</h2>
        
        <p>That's when I remembered. Twenty years ago, on this very night, 
        my twin brother had disappeared from this cabin. They never found 
        his body.</p>
        
        <p>*Knock, knock, knock.*</p>
        
        <p>"Let me in, brother. I've been waiting so long..."</p>
        
        <p>My hand reached for the doorknob, moving on its own. 
        Part of me wanted to open it. Part of me knew I shouldn't.</p>
        
        <p>But it was too late. The door was already opening...</p>
        """,
        story_type="scary",
        age_rating="15-20",
        reading_time=5,
        youtube_url="https://youtube.com/watch?v=example",
        tiktok_url="https://tiktok.com/@nomstory/video/example",
        instagram_url="https://instagram.com/reel/example"
    )
```

**Run workflow:**
```bash
python workflow.py
```

**Time:** 2-3 minutes per story (including translations)

### Step 6.2: Batch Publishing

Create file: `batch_publish.py`

```python
#!/usr/bin/env python3
"""
Batch publish multiple stories from JSON file
"""

import json
from workflow import publish_complete_story

def batch_publish_from_json(json_file: str):
    """
    Publish multiple stories from JSON file
    
    JSON format:
    {
        "stories": [
            {
                "title": "Story Title",
                "content": "<p>Story content...</p>",
                "story_type": "scary",
                "age_rating": "15-20",
                "reading_time": 5,
                "youtube_url": "https://...",
                "tiktok_url": "https://...",
                "instagram_url": "https://..."
            },
            ...
        ]
    }
    """
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stories = data.get('stories', [])
    total = len(stories)
    
    print(f"📚 Found {total} stories to publish")
    print("=" * 60)
    
    for i, story_data in enumerate(stories, 1):
        print(f"\n🔄 Publishing story {i}/{total}...")
        
        result = publish_complete_story(**story_data)
        
        if result:
            print(f"✅ Story {i}/{total} published successfully")
        else:
            print(f"❌ Story {i}/{total} failed")
        
        # Wait between stories to avoid overwhelming server
        if i < total:
            print("\n⏳ Waiting 30 seconds before next story...")
            time.sleep(30)
    
    print("\n" + "=" * 60)
    print(f"✅ Batch publish complete: {total} stories")
    print("=" * 60)

# Example usage
if __name__ == "__main__":
    batch_publish_from_json("stories.json")
```

**Create stories.json:**
```json
{
    "stories": [
        {
            "title": "The Haunted Attic",
            "content": "<p>Story content here...</p>",
            "story_type": "scary",
            "age_rating": "15-20",
            "reading_time": 4
        },
        {
            "title": "Family Secrets",
            "content": "<p>Story content here...</p>",
            "story_type": "family_drama",
            "age_rating": "20-25",
            "reading_time": 7
        }
    ]
}
```

**Run batch publish:**
```bash
python batch_publish.py
```

**Time:** ~3 minutes per story in batch

---

## Troubleshooting

### Common Issues

**Issue 1: REST API returns "rest_cannot_create"**
```
Solution:
- Check user has proper permissions (Administrator or Editor role)
- Verify authentication credentials
- Check .htaccess for redirect issues
```

**Issue 2: TranslatePress not translating**
```
Solution:
- Verify DeepL/Google API key is active
- Check API quota (500K chars/month free on DeepL)
- Clear WordPress cache
- Visit Settings → TranslatePress → General → Test API Key
```

**Issue 3: Custom fields not appearing in API**
```
Solution:
- Verify ACF "Show in REST API" is enabled for field group
- Clear permalinks: Settings → Permalinks → Save Changes
- Check if ACF Pro plugin is active (free version may have limitations)
```

**Issue 4: 404 errors on story URLs**
```
Solution:
- Flush permalinks: Settings → Permalinks → Save Changes
- Verify custom post type 'rewrite' => array('slug' => 'story')
- Check .htaccess file exists and is writable
```

**Issue 5: Slow translations**
```
Solution:
- Reduce number of languages being translated at once
- Upgrade to DeepL Pro API (faster)
- Enable caching plugin (WP Rocket)
- Increase PHP memory limit in wp-config.php:
  define('WP_MEMORY_LIMIT', '256M');
```

**Issue 6: Authentication fails**
```
Solution:
- Regenerate Application Password
- Check if HTTPS is enforced
- Verify no special characters in username
- Try JWT authentication as alternative
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor story publishing logs
- Check translation API quota
- Review site performance

**Weekly:**
- Backup WordPress database
- Update plugins (WordPress Admin → Updates)
- Review analytics

**Monthly:**
- Update WordPress core
- Check security logs (Wordfence)
- Optimize database (WP-Optimize plugin)
- Review DeepL API usage and costs

**Quarterly:**
- Review and renew licenses (TranslatePress, hosting)
- Update themes and plugins
- Performance audit

### Backup Strategy

**Automated Backups:**
```
1. Install UpdraftPlus plugin (free)
2. Settings → UpdraftPlus Backups
3. Schedule: Daily backups, retain 7 days
4. Remote storage: Google Drive, Dropbox, or S3
5. Include: Database, plugins, themes, uploads
```

**Manual API Backup:**
```python
# Backup all stories via API
import requests
import json

def backup_all_stories():
    response = requests.get(
        "https://nomstory.com/wp-json/wp/v2/stories?per_page=100",
        auth=("username", "app_password")
    )
    
    with open("stories_backup.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    
    print("✅ Backup complete: stories_backup.json")
```

### Performance Optimization

**Caching:**
```
1. Install WP Rocket ($49/year) or W3 Total Cache (free)
2. Enable:
   - Page caching
   - Browser caching
   - GZIP compression
   - CDN integration (Cloudflare free)
3. Result: 2-3x faster page loads
```

**Database Optimization:**
```
1. Install WP-Optimize plugin
2. Run weekly:
   - Clean post revisions (keep last 10)
   - Remove spam comments
   - Optimize database tables
```

**Image Optimization:**
```
1. Install Smush plugin (free)
2. Auto-optimize uploads
3. Convert to WebP format
4. Lazy loading enabled
```

---

## Summary

### What You've Accomplished

✅ **WordPress Installation** - Professional CMS setup  
✅ **Custom Post Type** - Dedicated story content type  
✅ **TranslatePress Setup** - 26-language translations with AI  
✅ **REST API Access** - Full programmatic control  
✅ **Publishing Scripts** - Automated story publishing  
✅ **Complete Workflow** - End-to-end automation  

### Publishing Workflow

**From story to 26 languages in ~50 minutes:**

1. Write story in English (30 min)
2. Run publishing script (30 seconds)
3. Automatic translation to 26 languages (5 min)
4. Review key languages (15 min)
5. Publish and share (5 min)

**Total:** 50 minutes vs 52-78 hours manual

### Next Steps

1. **Content Creation:** Start writing stories
2. **Video Integration:** Create TikTok/YouTube content
3. **SEO Optimization:** Optimize for search engines per language
4. **Analytics:** Set up Google Analytics for tracking
5. **Monetization:** Enable ads after reaching 50K pageviews
6. **Community:** Build email list and Discord server

### Resources

- WordPress Codex: https://codex.wordpress.org/
- REST API Handbook: https://developer.wordpress.org/rest-api/
- TranslatePress Docs: https://translatepress.com/docs/
- ACF Documentation: https://www.advancedcustomfields.com/resources/
- DeepL API: https://www.deepl.com/docs-api

---

**Questions or Issues?**  
Refer to Troubleshooting section or WordPress support forums.

**Ready to publish your first story?**  
Run: `python workflow.py`

🚀 **Good luck with NomStory!**
