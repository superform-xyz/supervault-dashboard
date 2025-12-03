// Initialize clipboard.js on all copy elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize clipboard.js on elements with data-clipboard-text attribute
    var clipboard = new ClipboardJS('[data-clipboard-text]');
    
    clipboard.on('success', function(e) {
        // If this is an icon element (i or svg)
        if (e.trigger.tagName === 'I' || e.trigger.tagName === 'SVG') {
            // Store original classes and color
            var originalClass = e.trigger.className;
            var originalStyle = e.trigger.getAttribute('style');
            
            // Change to check icon and green color
            e.trigger.className = 'fa fa-check';
            e.trigger.style.color = '#28a745'; // Bootstrap success green
            e.trigger.style.opacity = '1';
            
            // Reset after delay
            setTimeout(function() {
                e.trigger.className = originalClass;
                e.trigger.setAttribute('style', originalStyle);
            }, 1500);
        } else {
            // For other elements like buttons, change text
            var originalText = e.trigger.innerHTML;
            e.trigger.innerHTML = "Copied!";
            
            setTimeout(function() {
                e.trigger.innerHTML = originalText;
            }, 1500);
        }
        
        // Create a temporary tooltip
        var tooltip = document.createElement('div');
        tooltip.textContent = 'Copied!';
        tooltip.style.position = 'absolute';
        tooltip.style.background = 'rgba(0,0,0,0.8)';
        tooltip.style.color = 'white';
        tooltip.style.padding = '5px 10px';
        tooltip.style.borderRadius = '4px';
        tooltip.style.fontSize = '12px';
        tooltip.style.zIndex = '9999';
        tooltip.style.opacity = '0';
        tooltip.style.transition = 'opacity 0.3s';
        
        // Position near the element
        var rect = e.trigger.getBoundingClientRect();
        tooltip.style.top = (rect.top - 30) + 'px';
        tooltip.style.left = (rect.left + rect.width/2 - 30) + 'px';
        
        document.body.appendChild(tooltip);
        
        // Show then fade out
        setTimeout(function() { tooltip.style.opacity = '1'; }, 50);
        setTimeout(function() { 
            tooltip.style.opacity = '0'; 
            setTimeout(function() { document.body.removeChild(tooltip); }, 300);
        }, 1200);
        
        e.clearSelection();
    });
    
    clipboard.on('error', function(e) {
        console.error('Copy failed!');
    });
});
