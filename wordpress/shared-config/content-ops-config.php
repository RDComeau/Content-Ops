<?php
/**
 * Shared WordPress configuration for Content Ops
 * This file is included in all WordPress sites as a must-use plugin
 */

// Redis cache configuration
if (defined('WP_REDIS_HOST')) {
    define('WP_CACHE', true);
    define('WP_CACHE_KEY_SALT', 'content-ops');
}

// Security enhancements
define('DISALLOW_FILE_EDIT', true);
define('DISALLOW_FILE_MODS', false);
define('WP_AUTO_UPDATE_CORE', 'minor');

// Performance optimizations
define('WP_MEMORY_LIMIT', '256M');
define('WP_MAX_MEMORY_LIMIT', '512M');

// Database optimizations
define('WP_POST_REVISIONS', 5);
define('AUTOSAVE_INTERVAL', 300);
define('EMPTY_TRASH_DAYS', 30);

// Enable debug logging in non-production
if (!defined('WP_DEBUG')) {
    define('WP_DEBUG', false);
}

if (WP_DEBUG) {
    define('WP_DEBUG_LOG', true);
    define('WP_DEBUG_DISPLAY', false);
    define('SCRIPT_DEBUG', true);
}

// Cross-site functionality
add_action('init', function() {
    // Enable CORS for API requests between sites
    if (isset($_SERVER['HTTP_ORIGIN'])) {
        $allowed_origins = [
            'http://site1.localhost',
            'http://site2.localhost'
        ];
        
        if (in_array($_SERVER['HTTP_ORIGIN'], $allowed_origins)) {
            header('Access-Control-Allow-Origin: ' . $_SERVER['HTTP_ORIGIN']);
            header('Access-Control-Allow-Credentials: true');
            header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
            header('Access-Control-Allow-Headers: Content-Type, Authorization');
        }
    }
});

// Custom content sync hooks
add_action('save_post', function($post_id) {
    // Trigger content sync when important posts are saved
    $post = get_post($post_id);
    
    if ($post && in_array($post->post_type, ['post', 'page']) && $post->post_status === 'publish') {
        // Add to sync queue (this would be handled by the Python automation)
        wp_schedule_single_event(time() + 300, 'content_ops_sync_hook', [$post_id]);
    }
});

// Add custom REST API endpoints for automation
add_action('rest_api_init', function() {
    register_rest_route('content-ops/v1', '/health', [
        'methods' => 'GET',
        'callback' => function() {
            return [
                'status' => 'healthy',
                'timestamp' => current_time('mysql'),
                'site' => get_bloginfo('name'),
                'version' => get_bloginfo('version')
            ];
        },
        'permission_callback' => '__return_true'
    ]);
    
    register_rest_route('content-ops/v1', '/stats', [
        'methods' => 'GET',
        'callback' => function() {
            return [
                'posts' => wp_count_posts()->publish,
                'pages' => wp_count_posts('page')->publish,
                'users' => count_users()['total_users'],
                'comments' => wp_count_comments()->approved
            ];
        },
        'permission_callback' => '__return_true'
    ]);
});

// Cleanup and optimization hooks
add_action('wp_scheduled_delete', function() {
    // Clean up spam comments
    $spam_comments = get_comments(['status' => 'spam', 'number' => 100]);
    foreach ($spam_comments as $comment) {
        wp_delete_comment($comment->comment_ID, true);
    }
    
    // Clean up expired transients
    delete_expired_transients();
});

// Custom logging for automation
if (!function_exists('content_ops_log')) {
    function content_ops_log($message, $level = 'info') {
        if (WP_DEBUG_LOG) {
            error_log(sprintf('[Content-Ops] [%s] %s', strtoupper($level), $message));
        }
    }
}