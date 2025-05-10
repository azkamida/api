from flask import Flask, request, jsonify, send_file
import qrcode
import io

app = Flask(__name__)

# Fungsi menghitung CRC16 untuk QRIS
def calculate_crc16(qris_str):
    crc = 0xFFFF
    polynomial = 0x1021
    for b in qris_str.encode("ascii"):
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ polynomial) if (crc & 0x8000) else (crc << 1)
            crc &= 0xFFFF
    return format(crc, '04X')

# Fungsi untuk mengubah QRIS statis menjadi dinamis dengan nominal tertentu
def generate_qris_dinamis(original_qris, nominal):
    final_nominal_str = str(nominal)
    base_qris = original_qris.strip()[:-8].replace("010211", "010212")
    tag54 = f"54{len(final_nominal_str):02d}{final_nominal_str}"
    split = base_qris.split("5802ID")
    if len(split) != 2:
        raise ValueError("Format QRIS tidak valid: tag '5802ID' tidak ditemukan.")
    qris_with_amount = split[0] + tag54 + "5802ID" + split[1]
    full_qris = qris_with_amount + "6304" + calculate_crc16(qris_with_amount + "6304")
    return full_qris

# Endpoint: GET /amount/<nominal>
@app.route("/amount/<int:nominal>", methods=["GET"])
def generate_qris_by_amount(nominal):
    try:
        # QRIS statis kamu (ganti jika perlu)
        original_qris = "00020101021126670016COM.NOBUBANK.WWW01189360050300000879140214210379661725380303UMI51440014ID.CO.QRIS.WWW0215ID20253865385780303UMI5204541153033605802ID5922LUTIFY STORE OK23176316006BEKASI61051711162070703A0163041FF9"

        # Generate QRIS dinamis
        qris_string = generate_qris_dinamis(original_qris, nominal)

        # Generate QR code PNG
        img = qrcode.make(qris_string)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Kirim file gambar sebagai respon
        return send_file(img_io, mimetype='image/png', download_name=f'qris_{nominal}.png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Jalankan server
if __name__ == "__main__":
    app.run(debug=True)
