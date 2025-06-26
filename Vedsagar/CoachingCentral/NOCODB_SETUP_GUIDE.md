# NocoDB Setup Guide for EduCRM

## 1. NocoDB Installation Options

### Option A: Cloud (Recommended for beginners)
- Visit https://nocodb.com and sign up for a free account
- Create a new workspace and base

### Option B: Self-hosted (Docker)
```bash
docker run -d --name nocodb -p 8080:8080 nocodb/nocodb:latest
```

### Option C: Self-hosted (npm)
```bash
npm install -g nocodb
nocodb
```

## 2. Database Schema Setup

Once NocoDB is running, create the following tables with these exact field configurations:

### Table 1: categories
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| name | SingleLineText | Required, Unique |
| description | LongText | Optional |
| color | SingleLineText | Default: #1f77b4 |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 2: batches
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| name | SingleLineText | Required |
| category | SingleLineText | Required |
| start_date | Date | Required |
| end_date | Date | Optional |
| capacity | Number | Default: 30 |
| fee | Currency | Optional |
| schedule | SingleLineText | Optional |
| instructor | SingleLineText | Optional |
| description | LongText | Optional |
| whatsapp_group_link | URL | Optional |
| status | SingleSelect | Options: Active, Upcoming, Completed, Cancelled. Default: Active |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 3: students
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| full_name | SingleLineText | Required |
| parent_phone | PhoneNumber | Required |
| student_phone | PhoneNumber | Optional |
| email | Email | Optional |
| address | LongText | Optional |
| date_of_birth | Date | Optional |
| category | SingleLineText | Required |
| batch | SingleLineText | Required |
| batch_id | Number | Optional |
| total_fee | Currency | Default: 0 |
| paid_amount | Currency | Default: 0 |
| discount | Currency | Default: 0 |
| fee_due_date | Date | Optional |
| admission_date | Date | Default: today |
| status | SingleSelect | Options: Active, Inactive, Completed, Dropped. Default: Active |
| notes | LongText | Optional |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 4: tests
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| name | SingleLineText | Required |
| subject | SingleLineText | Optional |
| date | Date | Required |
| max_marks | Number | Required |
| category | SingleLineText | Required |
| batch | SingleLineText | Required |
| batch_id | Number | Optional |
| description | LongText | Optional |
| status | SingleSelect | Options: Scheduled, Completed, Cancelled. Default: Scheduled |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 5: test_scores
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| test_id | Number | Required |
| student_id | Number | Required |
| marks_obtained | Number | Required |
| attendance | SingleSelect | Options: Present, Absent. Default: Present |
| remarks | LongText | Optional |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 6: payments
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| student_id | Number | Required |
| amount | Currency | Required |
| payment_method | SingleSelect | Options: Cash, UPI, Bank Transfer, Cheque, Card, Online. Default: Cash |
| payment_date | Date | Required |
| transaction_reference | SingleLineText | Optional |
| notes | LongText | Optional |
| late_fee | Currency | Default: 0 |
| discount | Currency | Default: 0 |
| status | SingleSelect | Options: Completed, Pending, Failed, Refunded. Default: Completed |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 7: message_templates
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| name | SingleLineText | Required |
| category | SingleSelect | Options: General, Fee Reminder, Exam Notice, Holiday Notice, Admission. Default: General |
| type | SingleLineText | Optional |
| content | LongText | Required |
| is_active | Checkbox | Default: True |
| usage_count | Number | Default: 0 |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 8: communication_logs
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| timestamp | DateTime | Required |
| recipient_count | Number | Required |
| message_preview | LongText | Optional |
| template_used | SingleLineText | Optional |
| activity_type | SingleSelect | Options: whatsapp_message, email, sms, announcement. Default: whatsapp_message |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

### Table 9: activities
| Field Name | Field Type | Options/Settings |
|------------|------------|------------------|
| id | AutoNumber | Primary Key |
| description | LongText | Required |
| timestamp | DateTime | Required |
| activity_type | SingleSelect | Options: enrollment, payment, communication, system, test, batch. Default: system |
| created_at | DateTime | Default: now() |
| updated_at | DateTime | Default: now() |

## 3. Getting API Credentials

After creating all tables in NocoDB:

1. **Get API Token:**
   - Go to Account Settings (top right profile icon)
   - Click on "API Tokens"
   - Create new token and copy it

2. **Get Workspace ID:**
   - Look at the URL when you're in your workspace
   - Format: `https://app.nocodb.com/#/nc/{workspace_id}/`

3. **Get Base ID:**
   - Open your database base
   - Look at the URL: `https://app.nocodb.com/#/nc/{workspace_id}/{base_id}`

4. **Get Base URL:**
   - For cloud: `https://app.nocodb.com`
   - For self-hosted: `http://localhost:8080` (or your server URL)

## 4. Environment Variables Setup

Add these to your Replit Secrets or environment variables:

```
NOCODB_BASE_URL=https://app.nocodb.com
NOCODB_API_TOKEN=your_api_token_here
NOCODB_WORKSPACE_ID=your_workspace_id_here
NOCODB_BASE_ID=your_base_id_here
```

## 5. Initial Data Population

You can manually add some initial categories through NocoDB interface:

### Sample Categories:
1. **NEET Preparation**
   - Description: Medical entrance exam preparation
   - Color: #4CAF50

2. **JEE Main & Advanced**
   - Description: Engineering entrance exam preparation
   - Color: #2196F3

3. **UPSC Preparation**
   - Description: Civil services exam preparation
   - Color: #FF9800

### Sample Message Templates:
1. **Fee Reminder (Gentle)**
   - Category: Fee Reminder
   - Content: "Dear {student_name}, This is a gentle reminder that your fee payment of ₹{pending_amount} for {batch_name} is pending. Please make the payment at your earliest convenience."

2. **Exam Notice**
   - Category: Exam Notice
   - Content: "Dear {student_name}, This is to inform you about the upcoming {exam_name} on {exam_date}. Please prepare well and be present on time."

## 6. Testing the Connection

Once everything is set up:
1. Restart your EduCRM application
2. The system will automatically detect the NocoDB configuration
3. It will switch from demo mode to production mode
4. You can start adding real students, batches, and managing your coaching institute

## 7. Backup and Security

- **Regular Backups:** NocoDB cloud provides automatic backups
- **API Security:** Keep your API tokens secure and regenerate them periodically
- **Access Control:** Set up proper user roles and permissions in NocoDB
- **SSL/HTTPS:** Ensure your NocoDB instance uses HTTPS in production

## 8. Scaling Considerations

- **Performance:** NocoDB can handle thousands of records efficiently
- **Storage:** Monitor your data usage based on your plan
- **Concurrent Users:** Consider upgrading plans for multiple simultaneous users
- **API Limits:** Be aware of API rate limits in your NocoDB plan

Your EduCRM system will be fully functional once connected to NocoDB!