# Farm Visit Management System

A modern web application for managing farm visits with comprehensive data collection, admin panel, and PDF reporting capabilities.

## Features

### Farm Visit Form
- **Farmer Details**: Name, Farm ID, Phone, Location, GPS coordinates, Farm size, Farm type
- **Visit Details**: Date, Visit type, Officer name, Time spent
- **Observations**: Crops, Livestock, Issues, Photo upload, Video links
- **Recommendations**: Advice given
- **Follow-up**: Follow-up requirements, Training needs, Referrals

### Admin Panel
- View all farm visit records
- Search by farmer name, farm ID, or officer name
- Filter by visit type (Routine, Emergency, Follow-up)
- Download individual visit reports as PDF
- View uploaded photos in full size
- Modern, responsive design

### PDF Reports
- Complete visit information
- Embedded photos
- Professional formatting
- Downloadable from admin panel

## Installation

### Local Development

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional for local development):
   ```bash
   set FLASK_SECRET_KEY=your-secret-key-here
   set ADMIN_USERNAME=admin
   set ADMIN_PASSWORD=your-password
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   - Main form: http://localhost:5000
   - Admin panel: http://localhost:5000/admin

### Vercel Deployment

1. **Deploy to Vercel**:
   - Connect your repository to Vercel
   - The `vercel.json` file is already configured

2. **Set environment variables in Vercel dashboard**:
   - `FLASK_SECRET_KEY`: A secure random string
   - `ADMIN_USERNAME`: Your admin username
   - `ADMIN_PASSWORD`: Your admin password

3. **Important for Vercel deployment**:
   - Data is stored in memory (resets on each deployment)
   - Photos are stored as base64 in memory
   - No persistent file storage due to Vercel's read-only filesystem

## Usage

### Adding a Farm Visit
1. Navigate to the main page (http://localhost:5000)
2. Fill out all required fields in the form
3. Upload photos if available
4. Submit the form
5. Data will be saved to `visits.json`

### Managing Visits (Admin)
1. Navigate to the admin panel (http://localhost:5000/admin)
2. Use the search box to find specific visits
3. Filter by visit type using the dropdown
4. Click the PDF button to download a visit report
5. Click on photos to view them in full size

## File Structure

```
Farm/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── visits.json           # Data storage (created automatically)
├── templates/
│   ├── form.html         # Main visit form
│   └── admin.html        # Admin panel
├── static/
│   └── uploads/          # Uploaded photos
└── README.md             # This file
```

## Dependencies

- **Flask**: Web framework
- **ReportLab**: PDF generation
- **Pillow**: Image processing
- **Werkzeug**: File upload handling

## Data Storage

Visit data is stored in JSON format in `visits.json`. Each visit record includes:
- Unique ID
- All form fields
- Timestamp
- Photo filename (if uploaded)

## Security Notes

- This is a development application
- For production use, implement proper authentication
- Consider using a proper database instead of JSON
- Add input validation and sanitization
- Use HTTPS in production

## Customization

### Adding New Fields
1. Update the form in `templates/form.html`
2. Modify the `/submit_visit` route in `app.py`
3. Update the admin panel display in `templates/admin.html`
4. Adjust PDF generation in the `/download_pdf` route

### Styling
- CSS is embedded in the HTML templates
- Uses modern design with gradients and animations
- Fully responsive for mobile devices
- Font Awesome icons for visual elements

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py`
2. **File upload errors**: Check `static/uploads/` directory permissions
3. **PDF generation fails**: Ensure ReportLab is properly installed
4. **Photos not displaying**: Verify file paths and upload directory

### Debug Mode

The application runs in debug mode by default. To disable:
```python
app.run(debug=False)
```

## License

This project is open source and available under the MIT License.