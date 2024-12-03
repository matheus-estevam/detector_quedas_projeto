from cvzone.PoseModule import PoseDetector
import cv2
import cvzone
from twilio.rest import Client
import time

# Configure Twilio
account_sid = 'ACe4aa10e579228a40d139000d223462e1'  # Substitua pelo seu SID da conta Twilio
auth_token = '05fc2707d07d628290b71fa6e954bc06'  # Substitua pelo seu Auth Token
twilio_client = Client(account_sid, auth_token)
from_phone = '+19787189500'  # Número de telefone Twilio
to_phone = '+5581981797167'  # Seu número de telefone

# Inicialize o vídeo e o detector de poses
video = cv2.VideoCapture('vd01.mp4')
detector = PoseDetector()

queda_detectada = False  # Para evitar múltiplos envios do mesmo evento
tempo_exibicao = 0       # Controle do tempo de exibição da mensagem

while True:
    check, img = video.read()
    if not check:  # Verifique se o vídeo acabou
        break

    img = cv2.resize(img, (1280, 720))
    resultado = detector.findPose(img)
    pontos, bbox = detector.findPosition(img, draw=False)

    if len(pontos) >= 1:
        x, y, w, h = bbox['bbox']
        cabeca = pontos[0][1]
        joelho = pontos[26][1]
        diferenca = joelho - cabeca

        if diferenca <= 0 and not queda_detectada:
            cvzone.putTextRect(img, 'QUEDA DETECTADA!', (x, y - 80), scale=3, thickness=3, colorR=(0, 0, 255))
            queda_detectada = True
            tempo_exibicao = time.time() + 5  # Exibir mensagem por 5 segundos

            # Enviar SMS
            try:
                mensagem = twilio_client.messages.create(
                    body="Alerta! Uma queda foi detectada.",
                    from_=from_phone,
                    to=to_phone
                )
                print(f"SMS enviado com sucesso! ID da mensagem: {mensagem.sid}")
            except Exception as e:
                print(f"Erro ao enviar SMS: {e}")

    # Persistir a mensagem por 5 segundos após a detecção
    if queda_detectada and time.time() < tempo_exibicao:
        cvzone.putTextRect(img, 'QUEDA DETECTADA', (x, y - 80), scale=3, thickness=3, colorR=(0, 0, 255))

    cv2.imshow('IMG', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Saia ao pressionar 'q'
        break

video.release()
cv2.destroyAllWindows()
