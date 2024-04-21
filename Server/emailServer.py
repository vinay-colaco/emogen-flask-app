import credentials
import os
import random
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
report_id = ''.join(random.choices('0123456789', k=4))

subject = 'EMOGEN TESTING'
def email_body(file_name, predicted_emotion, predicted_gender, request_arrived, response_sent, time_taken_by_emotion_model, time_taken_by_gender_model):
    
    now = datetime.now()
    todays_date = now.strftime("%m/%d/%Y")

    return f"""
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Report Invoice</title>
        <script>
            function myFunction() {{
                window.print();
            }}
        </script>
        <style>
            .print{{
                margin:auto;
                max-width:900px;
            }}
            table {{background-image:url(cid:pic);}}
            
            .invoice-box{{
                    max-width:800px;
                    background:#ffffff;
                    margin:auto;
                    padding:30px;
                    border:1px solid #eee;
                    box-shadow:0 0 10px rgba(255, 254, 254, 0.15);
                    font-size:18px;
                    line-height:30px;
                    font-family:Georgia, 'Times New Roman', Times, serif;
                    color:#060505;
                }}
                
                .invoice-box table{{
                    width:100%;
                    line-height:inherit;
                    text-align:left;
                }}
                
                .invoice-box table td{{
                    padding:5px;
                    vertical-align:top;
                }}
                
                .invoice-box table tr td:nth-child(2){{
                    text-align:right;
                }}
                
                .invoice-box table tr.top table td{{
                    padding-bottom:20px;
                }}
                
                .invoice-box table tr.top table td.title{{
                    font-size:45px;
                    line-height:45px;
                    color:#333;
                }}
                
                .invoice-box table tr.information table td{{
                    padding-bottom:40px;
                }}
                
                .invoice-box table tr.heading td{{
                    background:#eee;
                    border-bottom:1px solid #ddd;
                    font-weight:bold;
                }}
                
                .invoice-box table tr.details td{{
                    padding-bottom:20px;
                }}
                
                .invoice-box table tr.item td{{
                    border-bottom:1px solid #eee;
                }}
                
                .invoice-box table tr.item.last td{{
                    border-bottom:none;
                }}
                
                .invoice-box table tr.total td:nth-child(2){{
                    border-top:2px solid #eee;
                    font-weight:bold;
                }}
                
                @media only screen and (max-width: 600px) {{
                    .invoice-box table tr.top table td{{
                        width:100%;
                        display:block;
                        text-align:center;
                    }}
                }}    
                    
                    .invoice-box table tr.information table td{{
                        width:100%;
                        display:block;
                        text-align:center;
                    }}
                    .back-video{{
                        position: absolute;
                        right: 0;
                        bottom: 0;
                        z-index: -1;
                    }}
                    @media (min-aspect-ratio: 16/9){{
                        .back-video{{
                            width: 100%;
                            height: auto;
                        }}
                    }}
                    @media (max-aspect-ratio: 16/9){{
                        .back-video{{
                            width: auto;
                            height: 100%;
                        }}
                    }}
        </style>
    </head>
    <body>
        <video autoplay loop muted plays-inline class="back-video">
            <source src="cid:bg1" type="video/mp4">
        </video>
        <div class="invoice-box">
            <table cellpadding="0" cellspacing="0">
                <tr class="top">
                    <td colspan="2">
                        <table>
                            <tr>
                                <td class="title">
                                    <img src="cid:logo" style="width:100%; max-width:280px;">
                                </td>
                                
                                <td>
                                    <b>Report ID: </b> {report_id}<br>
                                    <b>Date: </b> {todays_date}<br>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                
                <tr class="heading">
                    <td colspan="2"><center>ESTIMATION RESULT REPORT</center></td>
                </tr>
                
                <tr class="item">
                    <td>
                        <b>Audio File:</b>
                    </td>
                    
                    <td>
                        {file_name}
                    </td>
                </tr>
                
                <tr class="item">
                    <td>
                        <b>Predicted Emotion:</b>
                    </td>
                    
                    <td>
                        {predicted_emotion}
                    </td>
                </tr>

                <tr class="item">
                    <td>
                        <b>Predicted Gender:</b> 
                    </td>
                    
                    <td>
                        {predicted_gender}
                    </td>
                </tr>
                

                 <tr class="item">
                    <td>
                        <b>Request Sent At:</b>
                    </td>
                    
                    <td>
                        {request_arrived} 
                    </td>
                </tr>

                 <tr class="item">
                    <td>
                        <b>Response Sent At:</b>
                    </td>
                    
                    <td>
                        {response_sent}
                    </td>
                </tr>

                 <tr class="item">
                    <td>
                        <b>Time taken for predicting Emotion:</b>
                    </td>
                    
                    <td>
                        {time_taken_by_emotion_model:.2f} seconds
                    </td>
                </tr>

                <tr class="item">
                    <td>
                        <b>Time taken for predicting Gender:</b>
                    </td>
                    
                    <td>
                       {time_taken_by_gender_model:.2f} seconds
                    </td>
                </tr>
            </table>
        </div>
    </body>
</html>
"""

def email_service(file_name, predicted_emotion, predicted_gender, request_arrived, response_sent, time_taken_by_emotion_model, time_taken_by_gender_model):
    body = email_body(file_name, predicted_emotion, predicted_gender, request_arrived, response_sent, time_taken_by_emotion_model, time_taken_by_gender_model)
    msg = MIMEMultipart()
    msg['From'] = credentials.server_email
    msg['To'] = credentials.admin_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    image_path = 'logo.png'
    with open(image_path, 'rb') as image_file:
        image = MIMEImage(image_file.read(), name=os.path.basename(image_path))
        image.add_header('Content-ID', '<logo>')
        msg.attach(image)

    image_path = 'pic.png'
    with open(image_path, 'rb') as image_file:
        image = MIMEImage(image_file.read(), name=os.path.basename(image_path))
        image.add_header('Content-ID', '<pic>')
        msg.attach(image)

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()

    session.login(credentials.server_email, credentials.server_pass)

    session.sendmail(credentials.server_email,
                    credentials.admin_email, msg.as_string())
    print('Report Id:', report_id)
    print('Mail sent successfully')
    session.quit()
