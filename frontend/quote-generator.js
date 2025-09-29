/**
 * Quote PDF Generator
 * Generates professional PDF quotes using jsPDF
 */

class QuoteGenerator {
    constructor() {
        // Initialize jsPDF
        this.jsPDF = window.jspdf.jsPDF;

        // EmailJS configuration (using public key for demo)
        // You'll need to sign up at https://www.emailjs.com/ and get your own keys
        emailjs.init("YOUR_PUBLIC_KEY"); // Replace with your EmailJS public key

        // Company details
        this.company = {
            name: "CRELEC S.A.",
            email: "crelec@live.co.za",
            phone: "+27 11 444 4555",
            address: "Side Channel Blowers & Vacuum Pumps",
            website: "www.crelec.co.za"
        };
    }

    generatePDF(quoteData) {
        const doc = new this.jsPDF();
        const pageWidth = doc.internal.pageSize.width;
        const pageHeight = doc.internal.pageSize.height;

        // Colors
        const primaryColor = [26, 62, 76]; // Dark teal
        const textColor = [51, 51, 51];
        const lightGray = [128, 128, 128];

        // Header
        doc.setFillColor(...primaryColor);
        doc.rect(0, 0, pageWidth, 40, 'F');

        // Company Name
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(24);
        doc.setFont(undefined, 'bold');
        doc.text('CRELEC S.A.', 20, 20);

        doc.setFontSize(10);
        doc.setFont(undefined, 'normal');
        doc.text('SIDE CHANNEL BLOWERS & VACUUM PUMPS', 20, 28);
        doc.text('QUOTATION', pageWidth - 20, 28, { align: 'right' });

        // Quote details box
        doc.setTextColor(...textColor);
        doc.setFontSize(10);
        let y = 50;

        // Quote number and date
        doc.setFont(undefined, 'bold');
        doc.text('Quote Number:', 20, y);
        doc.setFont(undefined, 'normal');
        doc.text(quoteData.quote_id, 60, y);

        doc.setFont(undefined, 'bold');
        doc.text('Date:', 120, y);
        doc.setFont(undefined, 'normal');
        doc.text(new Date().toLocaleDateString(), 140, y);

        y += 7;
        doc.setFont(undefined, 'bold');
        doc.text('Valid Until:', 20, y);
        doc.setFont(undefined, 'normal');
        const validUntil = new Date();
        validUntil.setDate(validUntil.getDate() + 30);
        doc.text(validUntil.toLocaleDateString(), 60, y);

        // Client details
        y += 15;
        doc.setFillColor(245, 245, 245);
        doc.rect(15, y - 5, pageWidth - 30, 20, 'F');
        doc.setFont(undefined, 'bold');
        doc.text('CLIENT DETAILS', 20, y);
        y += 7;
        doc.setFont(undefined, 'normal');
        doc.text(`Email: ${quoteData.customer_data.email}`, 20, y);
        y += 7;
        doc.text(`Application: ${this.formatApplicationType(quoteData.customer_data.application || 'industrial')}`, 20, y);

        // Requirements Analysis
        y += 15;
        doc.setFillColor(245, 245, 245);
        doc.rect(15, y - 5, pageWidth - 30, 35, 'F');
        doc.setFont(undefined, 'bold');
        doc.text('REQUIREMENTS ANALYSIS', 20, y);
        y += 7;

        doc.setFont(undefined, 'normal');
        const calc = quoteData.calculation;
        const length = quoteData.customer_data.length || 0;
        const width = quoteData.customer_data.width || 0;
        const height = quoteData.customer_data.height || 0;
        doc.text(`Tank Dimensions: ${length}m × ${width}m × ${height}m`, 20, y);
        y += 6;
        doc.text(`Tank Volume: ${calc.tank_volume} m³`, 20, y);
        y += 6;
        const altitude = quoteData.customer_data.altitude || 0;
        doc.text(`Altitude: ${altitude}m above sea level`, 20, y);
        y += 6;
        const airflowHr = calc.airflow_required_hr || (calc.airflow_required * 60);
        doc.text(`Calculated Airflow: ${calc.airflow_required} m³/min (${airflowHr.toFixed(1)} m³/hr)`, 20, y);
        y += 6;
        doc.text(`Calculated Pressure: ${calc.pressure_required} mbar`, 20, y);
        y += 6;
        doc.text(`Power Estimate: ${calc.power_estimate} kW`, 20, y);

        // Recommended Products
        y += 15;
        doc.setFillColor(245, 245, 245);
        doc.rect(15, y - 5, pageWidth - 30, 10, 'F');
        doc.setFont(undefined, 'bold');
        doc.text('RECOMMENDED PRODUCTS', 20, y);
        y += 10;

        // Product details
        quoteData.products.forEach((match, index) => {
            const product = match.product;

            // Product header
            doc.setFillColor(240, 240, 240);
            doc.rect(15, y - 5, pageWidth - 30, 8, 'F');

            doc.setFont(undefined, 'bold');
            doc.setTextColor(...primaryColor);
            doc.text(`${index + 1}. ${product.model}`, 20, y);

            if (match.match_type === "Perfect Match") {
                doc.setTextColor(0, 128, 0);
                doc.text('★ BEST MATCH', pageWidth - 50, y);
            } else {
                doc.setTextColor(...lightGray);
                doc.text(match.match_type, pageWidth - 50, y);
            }

            y += 8;
            doc.setTextColor(...textColor);
            doc.setFont(undefined, 'normal');
            doc.setFontSize(9);

            // Product specs - handle both old and new format
            const airflowMin = product.airflow_m3_min || product.airflow_min / 60 || 0;
            const airflowMax = product.airflow_m3_max || product.airflow_max / 60 || airflowMin;
            const airflow = product.airflow_m3_min || product.airflow / 60 || 0;
            const pressure = product.pressure || ((product.pressure_min || 0) + (product.pressure_max || 0)) / 2;
            const power = product.power || 0;

            doc.text(`Airflow: ${airflow.toFixed(1)} m³/min (${(airflow * 60).toFixed(0)} m³/hr)`, 25, y);
            y += 5;
            doc.text(`Pressure: ${pressure.toFixed(0)} mbar`, 25, y);
            y += 5;
            doc.text(`Power: ${power} kW`, 25, y);
            y += 5;
            if (product.price) {
                doc.text(`Price: R ${product.price.toLocaleString()}`, 25, y);
            } else {
                doc.text(`Price: Contact for pricing`, 25, y);
            }

            // Stock status
            const stockStatus = this.getStockStatus(product);
            doc.setTextColor(...stockStatus.color);
            doc.text(`Status: ${stockStatus.text}`, 100, y - 10);

            doc.setTextColor(...textColor);
            doc.setFontSize(10);
            y += 10;
        });

        // Contact section
        y = pageHeight - 40;
        doc.line(20, y, pageWidth - 20, y);
        y += 5;

        doc.setFont(undefined, 'bold');
        doc.text('CONTACT US', 20, y);
        y += 7;

        doc.setFont(undefined, 'normal');
        doc.setFontSize(9);
        doc.text(`Email: ${this.company.email}`, 20, y);
        doc.text(`Phone: ${this.company.phone}`, 120, y);

        // Footer
        y = pageHeight - 20;
        doc.setTextColor(...lightGray);
        doc.setFontSize(8);
        doc.text('Terms & Conditions Apply', 20, y);
        doc.text('Powered by Liberlocus', pageWidth - 20, y, { align: 'right' });

        return doc;
    }

    formatApplicationType(type) {
        const types = {
            'waste_water': 'Waste Water Treatment',
            'fish_hatchery': 'Fish Hatchery / Aquaculture',
            'industrial': 'Industrial Process',
            'general': 'General Industrial'
        };
        return types[type] || 'General Application';
    }

    getStockStatus(product) {
        const inStock = product.in_stock || product.stock_status === 'in_stock';
        if (inStock) {
            return {
                text: '✓ In Stock - Immediate Delivery',
                color: [0, 128, 0]
            };
        } else if (product.stock_status === 'low_stock') {
            return {
                text: `⚠ Low Stock - ${product.delivery_days} days delivery`,
                color: [255, 140, 0]
            };
        } else {
            return {
                text: `⏱ On Order - ${product.delivery_days} days delivery`,
                color: [128, 128, 128]
            };
        }
    }

    async sendQuoteEmail(quoteData) {
        try {
            // Generate PDF
            const pdf = this.generatePDF(quoteData);
            const pdfBlob = pdf.output('blob');
            const pdfBase64 = await this.blobToBase64(pdfBlob);

            // Prepare email template parameters
            const templateParams = {
                to_email: quoteData.customer_data.email,
                cc_email: this.company.email,
                quote_id: quoteData.quote_id,
                customer_email: quoteData.customer_data.email,
                tank_dimensions: `${quoteData.customer_data.length}×${quoteData.customer_data.width}×${quoteData.customer_data.height}m`,
                airflow: quoteData.calculation.airflow_required,
                pressure: quoteData.calculation.pressure_required,
                products_list: this.formatProductsForEmail(quoteData.products),
                pdf_attachment: pdfBase64
            };

            // Send email using EmailJS
            // Note: You need to set up EmailJS with your own service
            const response = await emailjs.send(
                'YOUR_SERVICE_ID',  // Replace with your EmailJS service ID
                'YOUR_TEMPLATE_ID', // Replace with your EmailJS template ID
                templateParams
            );

            console.log('Email sent successfully:', response);
            return { success: true, message: 'Quote sent successfully!' };

        } catch (error) {
            console.error('Error sending email:', error);

            // Fallback: Download PDF locally
            const pdf = this.generatePDF(quoteData);
            pdf.save(`Quote_${quoteData.quote_id}.pdf`);

            return {
                success: false,
                message: 'Email service temporarily unavailable. Quote downloaded to your device.',
                downloaded: true
            };
        }
    }

    formatProductsForEmail(products) {
        return products.map((match, index) => {
            const p = match.product;
            return `${index + 1}. ${p.model} - R${p.price.toLocaleString()} - ${p.stock_status}`;
        }).join('\n');
    }

    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    // Alternative: Direct download for testing
    downloadPDF(quoteData) {
        const pdf = this.generatePDF(quoteData);
        pdf.save(`Crelec_Quote_${quoteData.quote_id}.pdf`);
    }
}