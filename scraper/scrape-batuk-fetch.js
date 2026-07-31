const fs = require('fs');

(async () => {
  console.log('Starting Batuk scraper with fetch...\n');

  const url = 'https://www.batuk.com.ar/hombre/abrigos/';

  try {
    console.log(`Fetching ${url}`);
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const html = await response.text();
    console.log(`Received ${html.length} bytes of HTML\n`);

    // Save HTML for inspection
    fs.writeFileSync('page.html', html);
    console.log('Saved HTML to page.html for inspection\n');

    // Simple regex-based extraction for product data
    const products = [];

    // Look for product containers - adjust selector based on HTML structure
    // Try to find common patterns
    const productPattern = /(?:<li[^>]*class="[^"]*product[^"]*"[^>]*>|<div[^>]*class="[^"]*product[^"]*"[^>]*>)([\s\S]*?)(?:<\/li>|<\/div>)/gi;
    const linkPattern = /<a[^>]*href="([^"]*)"[^>]*>/gi;
    const imgPattern = /<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"/gi;
    const pricePattern = /\$([\d,]+(?:\.\d{2})?)/g;

    // More general approach - extract all product links and images
    const links = [];
    let match;

    // Find all product URLs (usually contain /producto/ in the URL)
    const urlRegex = /<a[^>]*href="([^"]*\/producto\/[^"]*)"[^>]*>/gi;
    while ((match = urlRegex.exec(html)) !== null) {
      const url = match[1];
      // Make it absolute if relative
      const absoluteUrl = url.startsWith('http') ? url : new URL(url, 'https://www.batuk.com.ar').href;
      links.push(absoluteUrl);
    }

    console.log(`Found ${links.length} product links\n`);

    // Extract images and prices nearby
    const images = [];
    const imgRegex = /<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"/gi;
    while ((match = imgRegex.exec(html)) !== null) {
      if (match[1].includes('producto') || match[1].includes('product') || match[1].includes('image')) {
        images.push({
          src: match[1],
          alt: match[2]
        });
      }
    }

    console.log(`Found ${images.length} product images\n`);

    // Try to extract prices - look for currency pattern
    const prices = [];
    const priceRegex = /\$\s*([\d,]+(?:\.\d{2})?)/g;
    while ((match = priceRegex.exec(html)) !== null) {
      prices.push(match[1]);
    }

    console.log(`Found ${prices.length} prices\n`);

    // If links found, pair them with images and prices
    if (links.length > 0) {
      links.slice(0, Math.max(images.length, prices.length)).forEach((link, i) => {
        products.push({
          title: images[i]?.alt || `Product ${i + 1}`,
          price: prices[i] ? `$${prices[i]}` : 'N/A',
          image: images[i]?.src || null,
          url: link
        });
      });
    }

    console.log(`Extracted ${products.length} products\n`);

    if (products.length > 0) {
      products.forEach((product, index) => {
        console.log(`\n${index + 1}. ${product.title}`);
        console.log(`   Price: ${product.price}`);
        console.log(`   URL: ${product.url}`);
        console.log(`   Image: ${product.image || 'N/A'}`);
      });
    } else {
      console.log('No products extracted. The HTML structure might be different.');
      console.log('Check page.html for the actual page structure.');
    }

    // Save to JSON
    const outputData = {
      url: url,
      timestamp: new Date().toISOString(),
      totalProducts: products.length,
      products: products
    };

    fs.writeFileSync('batuk-products.json', JSON.stringify(outputData, null, 2));
    console.log('\n\nData saved to batuk-products.json');

    // Save to CSV
    if (products.length > 0) {
      const csv = [
        ['Title', 'Price', 'URL', 'Image'].join(',')
      ].concat(
        products.map(p => [
          `"${(p.title || '').replace(/"/g, '""')}"`,
          `"${(p.price || '').replace(/"/g, '""')}"`,
          `"${(p.url || '').replace(/"/g, '""')}"`,
          `"${(p.image || '').replace(/"/g, '""')}"`
        ].join(','))
      ).join('\n');

      fs.writeFileSync('batuk-products.csv', csv);
      console.log('Data saved to batuk-products.csv');
    }

  } catch (error) {
    console.error('Error:', error.message);
  }

  console.log('\nScraper completed!');
})();
