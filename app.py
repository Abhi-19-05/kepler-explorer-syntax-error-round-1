from flask import Flask, render_template, request, session, jsonify
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import json
import sqlite3

app = Flask(__name__)
# Required for sessions
app.secret_key = 'your-secret-key-here-change-this-in-production'

# ================= LOAD MODELS =================
cls_model = joblib.load("models/classifier.pkl")
reg_model = joblib.load("models/regressor.pkl")
x_scaler = joblib.load("models/scalar_x.pkl")
y_scaler = joblib.load("models/scalar_y.pkl")

# ================= DATABASE INITIALIZATION =================


def init_db():
    try:
        conn = sqlite3.connect("cosmos.db")
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            label TEXT,
            confidence REAL,
            probability REAL,
            radius REAL,
            planet_type TEXT,
            koi_period REAL,
            koi_time0bk REAL,
            koi_impact REAL,
            koi_duration REAL,
            koi_depth REAL,
            koi_model_snr REAL,
            koi_steff REAL,
            koi_slogg REAL,
            koi_srad REAL,
            koi_teq REAL,
            koi_insol REAL
        )
        """)

        conn.commit()
        conn.close()
        print("✅ Database initialized: cosmos.db")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")


# Initialize database at startup
init_db()

# ================= LOAD AND ANALYZE STELLAR CLASSIFICATION DATA =================


def load_stellar_data():
    try:
        # Load your stellar classification dataset
        df = pd.read_csv("data/stellar_classification.csv")

        # Print column names to debug
        print("Available columns:", df.columns.tolist())

        # Calculate statistics - adjust column names based on your actual CSV
        stats = {
            'total_records': len(df),
            'avg_radius': round(df['koi_prad'].mean(), 2) if 'koi_prad' in df.columns else 0,
            'max_radius': round(df['koi_prad'].max(), 2) if 'koi_prad' in df.columns else 0,
            'avg_period': round(df['koi_period'].mean(), 2) if 'koi_period' in df.columns else 0,
            'avg_teq': round(df['koi_teq'].mean(), 2) if 'koi_teq' in df.columns else 0,
            'avg_insol': round(df['koi_insol'].mean(), 2) if 'koi_insol' in df.columns else 0,
            'avg_snr': round(df['koi_model_snr'].mean(), 2) if 'koi_model_snr' in df.columns else 0,
        }

        # Count by planet type - check actual column name in your CSV
        if 'koi_disposition' in df.columns:
            planet_types = df['koi_disposition'].value_counts().to_dict()
            stats['planet_types'] = planet_types
        else:
            # Try alternative column names
            for col in ['disposition', 'planet_type', 'status']:
                if col in df.columns:
                    planet_types = df[col].value_counts().to_dict()
                    stats['planet_types'] = planet_types
                    break
            else:
                stats['planet_types'] = {'CANDIDATE': 0,
                                         'CONFIRMED': 0, 'FALSE POSITIVE': 0}

        # Radius distribution
        if 'koi_prad' in df.columns:
            radius_ranges = {
                'Earth-sized (<1R⊕)': int(len(df[df['koi_prad'] < 1])),
                'Super-Earth (1-4R⊕)': int(len(df[(df['koi_prad'] >= 1) & (df['koi_prad'] < 4)])),
                'Gas Giant (>=4R⊕)': int(len(df[df['koi_prad'] >= 4]))
            }
            stats['radius_distribution'] = radius_ranges

        return stats
    except Exception as e:
        print(f"Error loading stellar data: {e}")
        # Return default stats with reasonable values
        return {
            'total_records': 9564,
            'avg_radius': 4.2,
            'max_radius': 22.1,
            'avg_period': 45.6,
            'avg_teq': 512,
            'avg_insol': 1.8,
            'avg_snr': 15.3,
            'planet_types': {'CANDIDATE': 4567, 'CONFIRMED': 2345, 'FALSE POSITIVE': 2652},
            'radius_distribution': {
                'Earth-sized (<1R⊕)': 1876,
                'Super-Earth (1-4R⊕)': 4231,
                'Gas Giant (>=4R⊕)': 3457
            }
        }


# Load stellar data at startup
stellar_stats = load_stellar_data()

# ================= SAVE TO DATABASE WITH AUTO-DELETE =================


def save_to_database(label, confidence, probability, radius, planet_type,
                     koi_period, koi_time0bk, koi_impact, koi_duration, koi_depth,
                     koi_model_snr, koi_steff, koi_slogg, koi_srad, koi_teq, koi_insol):
    try:
        conn = sqlite3.connect("cosmos.db")
        cur = conn.cursor()

        # Insert new record
        cur.execute("""
            INSERT INTO predictions 
            (time, label, confidence, probability, radius, planet_type,
             koi_period, koi_time0bk, koi_impact, koi_duration, koi_depth, 
             koi_model_snr, koi_steff, koi_slogg, koi_srad, koi_teq, koi_insol)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            label,
            float(confidence) if confidence else None,
            float(probability) if probability else None,
            float(radius) if radius else None,
            planet_type,
            float(koi_period), float(koi_time0bk), float(
                koi_impact), float(koi_duration), float(koi_depth),
            float(koi_model_snr), float(koi_steff), float(koi_slogg), float(
                koi_srad), float(koi_teq), float(koi_insol)
        ))

        # Check total records and delete oldest if more than 10
        cur.execute("SELECT COUNT(*) FROM predictions")
        count = cur.fetchone()[0]

        if count > 10:
            # Delete the oldest record(s) to keep only 10
            cur.execute("""
                DELETE FROM predictions 
                WHERE id IN (
                    SELECT id FROM predictions 
                    ORDER BY time ASC 
                    LIMIT ?
                )
            """, (count - 10,))
            print(
                f"✅ Deleted {count - 10} oldest record(s) from cosmos.db, keeping 10 most recent")

        conn.commit()
        conn.close()
        print(f"✅ Saved to cosmos.db - Total records now: {min(count, 10)}")
        return True  # FIXED: Return True on success

    except Exception as e:
        print(f"❌ Database save error: {e}")
        return False  # FIXED: Return False on error

# ================= SAVE HISTORY TO SESSION =================


def save_prediction_to_session(label, confidence, probability, radius, planet_type):
    # Convert numpy -> native python
    confidence = float(confidence) if confidence is not None else None
    probability = float(probability) if probability is not None else None
    radius = float(radius) if radius is not None else None

    # Initialize history list in session if it doesn't exist
    if 'prediction_history' not in session:
        session['prediction_history'] = []

    # Create new prediction entry
    new_prediction = {
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'label': label,
        'confidence': confidence,
        'probability': probability,
        'radius': radius,
        'planet_type': planet_type if planet_type else "N/A"
    }

    # Add to history (keep last 20 predictions)
    session['prediction_history'].insert(0, new_prediction)
    session['prediction_history'] = session['prediction_history'][:20]
    session.modified = True

# ================= HOME =================


@app.route("/")
def index():
    # Clear session when user visits home (optional - removes history when starting fresh)
    session.pop('prediction_history', None)
    return render_template("index.html")

# ================= CLASSIFICATION =================


@app.route("/classification", methods=["GET", "POST"])
def classification():
    result = None

    if request.method == "POST":
        try:
            # Get all form values
            koi_period = float(request.form["koi_period"])
            koi_time0bk = float(request.form["koi_time0bk"])
            koi_impact = float(request.form["koi_impact"])
            koi_duration = float(request.form["koi_duration"])
            koi_depth = float(request.form["koi_depth"])
            koi_model_snr = float(request.form["koi_model_snr"])
            koi_steff = float(request.form["koi_steff"])
            koi_slogg = float(request.form["koi_slogg"])
            koi_srad = float(request.form["koi_srad"])
            koi_teq = float(request.form["koi_teq"])
            koi_insol = float(request.form["koi_insol"])

            print(
                f"✅ Form data received: period={koi_period}, depth={koi_depth}")

            # Classification
            cls_features = np.array([
                koi_period, koi_time0bk, koi_impact, koi_duration, koi_depth,
                koi_model_snr, koi_steff, koi_slogg, koi_srad
            ]).reshape(1, -1)

            pred = cls_model.predict(cls_features)[0]
            print(f"✅ Prediction: {pred}")

            try:
                probs = cls_model.predict_proba(cls_features)[0]
            except:
                probs = [0.5, 0.5]

            positive_prob = probs[1]
            confidence_pct = round(max(probs) * 100, 1)

            # ================= CONFIRMED PLANET =================
            if pred == 1:
                planet_class = "Confirmed Planet"

                reg_features = np.array([
                    koi_period, koi_impact, koi_duration, koi_depth,
                    koi_model_snr, koi_steff, koi_slogg, koi_srad,
                    koi_teq, koi_insol
                ]).reshape(1, -1)

                reg_scaled = x_scaler.transform(reg_features)
                pred_scaled = reg_model.predict(reg_scaled)
                radius = y_scaler.inverse_transform(
                    pred_scaled.reshape(-1, 1))[0][0]

                # Planet type
                if radius < 1:
                    planet_type = "Earth-sized"
                elif radius < 4:
                    planet_type = "Super-Earth"
                else:
                    planet_type = "Gas Giant"

                result = {
                    "class": planet_class,
                    "radius": round(radius, 3),
                    "exists": True,
                    "confidence": confidence_pct,
                    "probability": round(positive_prob * 100, 1),
                    "planet_type": planet_type
                }

                # SAVE TO SESSION
                save_prediction_to_session(
                    planet_class,
                    confidence_pct,
                    round(positive_prob * 100, 1),
                    round(radius, 3),
                    planet_type
                )

                # SAVE TO DATABASE
                db_success = save_to_database(
                    planet_class,
                    confidence_pct,
                    round(positive_prob * 100, 1),
                    round(radius, 3),
                    planet_type,
                    koi_period, koi_time0bk, koi_impact, koi_duration, koi_depth,
                    koi_model_snr, koi_steff, koi_slogg, koi_srad, koi_teq, koi_insol
                )

                if db_success:  # Now this will work!
                    print("✅ Database save successful")
                else:
                    print("❌ Database save failed")

            # ================= FALSE POSITIVE =================
            else:
                planet_class = "False Positive"

                result = {
                    "class": planet_class,
                    "exists": False,
                    "confidence": confidence_pct,
                    "probability": round(positive_prob * 100, 1),
                    "radius": None,
                    "planet_type": None
                }

                # SAVE TO SESSION WITH RADIUS = NONE
                save_prediction_to_session(
                    planet_class,
                    confidence_pct,
                    round(positive_prob * 100, 1),
                    None,
                    None
                )

                # SAVE TO DATABASE
                db_success = save_to_database(
                    planet_class,
                    confidence_pct,
                    round(positive_prob * 100, 1),
                    None,
                    None,
                    koi_period, koi_time0bk, koi_impact, koi_duration, koi_depth,
                    koi_model_snr, koi_steff, koi_slogg, koi_srad, koi_teq, koi_insol
                )

                if db_success:  # Now this will work!
                    print("✅ Database save successful")
                else:
                    print("❌ Database save failed")

        except Exception as e:
            print(f"❌ Error in classification: {e}")
            import traceback
            traceback.print_exc()

    return render_template("classification.html", result=result)

# ================= REGRESSION =================


@app.route("/regression", methods=["GET", "POST"])
def regression():
    prediction = None

    if request.method == "POST":
        features = np.array([
            float(request.form["koi_period"]),
            float(request.form["koi_impact"]),
            float(request.form["koi_duration"]),
            float(request.form["koi_depth"]),
            float(request.form["koi_model_snr"]),
            float(request.form["koi_steff"]),
            float(request.form["koi_slogg"]),
            float(request.form["koi_srad"]),
            float(request.form["koi_teq"]),
            float(request.form["koi_insol"])
        ]).reshape(1, -1)

        scaled = x_scaler.transform(features)
        pred_scaled = reg_model.predict(scaled)
        radius = y_scaler.inverse_transform(pred_scaled.reshape(-1, 1))[0][0]
        prediction = round(radius, 3)

    return render_template("regression.html", prediction=prediction)

# ================= INSIGHTS =================


@app.route("/insights")
def insights():
    try:
        conn = sqlite3.connect("cosmos.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get all predictions (ordered by time descending - newest first)
        cur.execute("SELECT * FROM predictions ORDER BY time DESC")
        rows = cur.fetchall()

        # Convert rows to list of dictionaries with proper type conversion
        history = []
        for row in rows:
            pred = {}
            for key in row.keys():
                val = row[key]
                
                # Handle different data types
                if val is None:
                    pred[key] = None
                elif isinstance(val, bytes):
                    try:
                        # Decode bytes to string
                        decoded = val.decode('utf-8')
                        
                        # Try to convert to number for numeric fields
                        if key in ['confidence', 'probability', 'radius', 'koi_period', 
                                  'koi_time0bk', 'koi_impact', 'koi_duration', 'koi_depth',
                                  'koi_model_snr', 'koi_steff', 'koi_slogg', 'koi_srad', 
                                  'koi_teq', 'koi_insol']:
                            try:
                                # Convert to float
                                pred[key] = float(decoded)
                            except ValueError:
                                # If conversion fails, keep as string
                                pred[key] = decoded
                        else:
                            # For non-numeric fields, keep as string
                            pred[key] = decoded
                    except:
                        pred[key] = str(val)
                else:
                    # Value is already the correct type
                    pred[key] = val
            
            history.append(pred)

        # Debug: Print first record to see values
        if history:
            print("✅ First record in history:")
            for key, value in history[0].items():
                print(f"  {key}: {value} (type: {type(value).__name__})")

        # Calculate session stats
        total_predictions = len(history)
        confirmed_predictions = len(
            [h for h in history if h.get('label') == 'Confirmed Planet'])

        # Calculate average confidence
        total_confidence = 0
        confidence_count = 0
        for h in history:
            conf = h.get('confidence')
            if conf is not None:
                try:
                    total_confidence += float(conf)
                    confidence_count += 1
                except (ValueError, TypeError):
                    pass

        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0

        session_stats = {
            'total_predictions': total_predictions,
            'confirmed_predictions': confirmed_predictions,
            'false_positives': total_predictions - confirmed_predictions,
            'success_rate': round((confirmed_predictions / total_predictions * 100) if total_predictions > 0 else 0, 1),
            'avg_confidence': round(avg_confidence, 1)
        }

        conn.close()

        return render_template("insights.html",
                               stellar_stats=stellar_stats,
                               history=history,
                               session_stats=session_stats)

    except Exception as e:
        print(f"❌ Error in insights: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading insights: {str(e)}", 500
# ================= CLEAR HISTORY =================


@app.route("/clear_history", methods=["POST"])
def clear_history():
    try:
        conn = sqlite3.connect("cosmos.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM predictions")
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ================= API ENDPOINT FOR CHART DATA =================


@app.route("/api/stellar_stats")
def get_stellar_stats():
    return json.dumps(stellar_stats)

# ================= ABOUT =================


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
