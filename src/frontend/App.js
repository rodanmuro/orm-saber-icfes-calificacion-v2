import { StatusBar } from 'expo-status-bar';
import { useMemo, useState } from 'react';
import * as ImagePicker from 'expo-image-picker';
import * as ImageManipulator from 'expo-image-manipulator';
import {
  ActivityIndicator,
  Image,
  Modal,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import {
  buildHealthUrl,
  buildOcrReadUrl,
  getApiBaseUrl,
  getDefaultMetadataPath,
} from './src/config/api';
import { checkHealth } from './src/services/health';
import { sendPhotoToOcr } from './src/services/omrRead';

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(getApiBaseUrl());
  const [metadataPath, setMetadataPath] = useState(getDefaultMetadataPath());
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [photoUri, setPhotoUri] = useState('');
  const [photoPreviewVisible, setPhotoPreviewVisible] = useState(false);
  const [omrLoading, setOmrLoading] = useState(false);
  const [omrResult, setOmrResult] = useState(null);
  const healthUrl = useMemo(() => buildHealthUrl(apiBaseUrl), [apiBaseUrl]);
  const omrReadUrl = useMemo(() => buildOcrReadUrl(apiBaseUrl), [apiBaseUrl]);

  async function handleHealthCheck() {
    if (!healthUrl) {
      setResult({
        type: 'error',
        title: 'URL inválida',
        detail: 'Debes ingresar una URL base válida del backend.',
      });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await checkHealth(healthUrl);
      if (response.ok) {
        setResult({
          type: 'success',
          title: 'Conexión exitosa',
          detail: `Backend respondió ${response.statusCode}`,
          payload: response.payload,
        });
      } else {
        setResult({
          type: 'error',
          title: 'Backend alcanzable pero con error',
          detail: `HTTP ${response.statusCode}`,
          payload: response.payload,
        });
      }
    } catch (error) {
      setResult({
        type: 'error',
        title: 'No se pudo conectar',
        detail: String(error?.message || error),
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleTakePhoto() {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (permission.status !== 'granted') {
      setOmrResult({
        type: 'error',
        title: 'Permiso de cámara denegado',
        detail: 'Debes permitir cámara para tomar la foto.',
      });
      return;
    }

    const capture = await ImagePicker.launchCameraAsync({
      cameraType: ImagePicker.CameraType.back,
      quality: 0.85,
      allowsEditing: false,
      exif: true,
    });

    if (capture.canceled || !capture.assets?.length) {
      return;
    }

    const asset = capture.assets[0];
    const normalizedUri = await normalizePhotoOrientation(asset);
    setPhotoUri(normalizedUri);
    setOmrResult(null);
  }

  async function normalizePhotoOrientation(asset) {
    const orientation = Number(asset?.exif?.Orientation || 1);
    const rotate =
      orientation === 3
        ? 180
        : orientation === 6
          ? 90
          : orientation === 8
            ? 270
            : 0;

    if (!rotate) {
      return asset.uri;
    }

    const normalized = await ImageManipulator.manipulateAsync(
      asset.uri,
      [{ rotate }],
      { compress: 0.95, format: ImageManipulator.SaveFormat.JPEG }
    );
    return normalized.uri;
  }

  async function handleSendPhoto() {
    if (!omrReadUrl) {
      setOmrResult({
        type: 'error',
        title: 'URL inválida',
        detail: 'Configura URL base del backend antes de enviar.',
      });
      return;
    }
    if (!photoUri) {
      setOmrResult({
        type: 'error',
        title: 'Falta foto',
        detail: 'Toma una foto antes de enviar al backend.',
      });
      return;
    }

    setOmrLoading(true);
    setOmrResult(null);
    try {
      const response = await sendPhotoToOcr({
        endpointUrl: omrReadUrl,
        photoUri,
        metadataPath,
      });
      if (response.ok) {
        setOmrResult({
          type: 'success',
          title: 'Lectura OMR completada',
          detail: `Backend respondió ${response.statusCode}`,
          payload: response.payload,
        });
      } else {
        setOmrResult({
          type: 'error',
          title: 'Error en lectura OMR',
          detail: `HTTP ${response.statusCode}`,
          payload: response.payload,
        });
      }
    } catch (error) {
      setOmrResult({
        type: 'error',
        title: 'No se pudo enviar la foto',
        detail: String(error?.message || error),
      });
    } finally {
      setOmrLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>OMR LAN Check</Text>
        <Text style={styles.subtitle}>
          Prueba conectividad celular - backend local
        </Text>

        <View style={styles.card}>
          <Text style={styles.label}>URL base del backend</Text>
          <TextInput
            style={styles.input}
            value={apiBaseUrl}
            onChangeText={setApiBaseUrl}
            autoCapitalize="none"
            autoCorrect={false}
            placeholder="http://192.168.1.10:8000/api/v1"
          />
          <Text style={styles.urlHint}>Health URL: {healthUrl || '-'}</Text>

          <Pressable
            onPress={handleHealthCheck}
            disabled={loading}
            style={[styles.button, loading && styles.buttonDisabled]}
          >
            {loading ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text style={styles.buttonText}>Probar conexión</Text>
            )}
          </Pressable>
        </View>

        {result ? (
          <View
            style={[
              styles.resultCard,
              result.type === 'success' ? styles.successCard : styles.errorCard,
            ]}
          >
            <Text style={styles.resultTitle}>{result.title}</Text>
            <Text style={styles.resultDetail}>{result.detail}</Text>
            {result.payload ? (
              <Text style={styles.resultPayload}>
                {JSON.stringify(result.payload, null, 2)}
              </Text>
            ) : null}
          </View>
        ) : null}

        <View style={styles.card}>
          <Text style={styles.label}>Captura y envío OMR</Text>
          <Text style={styles.urlHint}>Endpoint: {omrReadUrl || '-'}</Text>
          <TextInput
            style={styles.input}
            value={metadataPath}
            onChangeText={setMetadataPath}
            autoCapitalize="none"
            autoCorrect={false}
            placeholder="data/output/template_basica_omr_v1.json"
          />

          <Pressable onPress={handleTakePhoto} style={styles.secondaryButton}>
            <Text style={styles.secondaryButtonText}>Tomar foto</Text>
          </Pressable>

          {photoUri ? (
            <>
              <Pressable onPress={() => setPhotoPreviewVisible(true)}>
                <Image
                  source={{ uri: photoUri }}
                  style={styles.previewImage}
                  resizeMode="contain"
                />
              </Pressable>
              <Text style={styles.urlHint}>Toca la imagen para verla completa.</Text>
            </>
          ) : (
            <Text style={styles.urlHint}>Aún no has tomado foto.</Text>
          )}

          <Pressable
            onPress={handleSendPhoto}
            disabled={omrLoading}
            style={[styles.button, omrLoading && styles.buttonDisabled]}
          >
            {omrLoading ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text style={styles.buttonText}>Enviar foto a backend</Text>
            )}
          </Pressable>
        </View>

        {omrResult ? (
          <View
            style={[
              styles.resultCard,
              omrResult.type === 'success' ? styles.successCard : styles.errorCard,
            ]}
          >
            <Text style={styles.resultTitle}>{omrResult.title}</Text>
            <Text style={styles.resultDetail}>{omrResult.detail}</Text>
            {omrResult.payload?.quality_summary ? (
              <Text style={styles.resultDetail}>
                Resumen: {JSON.stringify(omrResult.payload.quality_summary)}
              </Text>
            ) : null}
            {omrResult.payload ? (
              <Text style={styles.resultPayload}>
                {JSON.stringify(omrResult.payload, null, 2)}
              </Text>
            ) : null}
          </View>
        ) : null}
      </ScrollView>
      <Modal
        animationType="fade"
        transparent={false}
        visible={photoPreviewVisible}
        onRequestClose={() => setPhotoPreviewVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <Pressable
            style={styles.modalCloseButton}
            onPress={() => setPhotoPreviewVisible(false)}
          >
            <Text style={styles.modalCloseText}>Cerrar</Text>
          </Pressable>
          {photoUri ? (
            <Image
              source={{ uri: photoUri }}
              style={styles.modalImage}
              resizeMode="contain"
            />
          ) : null}
        </SafeAreaView>
      </Modal>
      <StatusBar style="auto" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  container: {
    padding: 20,
    gap: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#111827',
  },
  subtitle: {
    fontSize: 14,
    color: '#374151',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 14,
    gap: 10,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1f2937',
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 9,
    fontSize: 14,
    color: '#111827',
    backgroundColor: '#ffffff',
  },
  urlHint: {
    fontSize: 12,
    color: '#4b5563',
  },
  button: {
    marginTop: 6,
    backgroundColor: '#0f766e',
    paddingVertical: 11,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#6b7280',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '600',
  },
  secondaryButton: {
    marginTop: 4,
    backgroundColor: '#1d4ed8',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  previewImage: {
    marginTop: 4,
    width: '100%',
    height: 260,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#d1d5db',
    backgroundColor: '#e5e7eb',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#000000',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 12,
  },
  modalCloseButton: {
    alignSelf: 'flex-end',
    marginBottom: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#1f2937',
  },
  modalCloseText: {
    color: '#ffffff',
    fontWeight: '600',
    fontSize: 14,
  },
  modalImage: {
    width: '100%',
    height: '90%',
  },
  resultCard: {
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    gap: 7,
  },
  successCard: {
    backgroundColor: '#ecfdf5',
    borderColor: '#6ee7b7',
  },
  errorCard: {
    backgroundColor: '#fef2f2',
    borderColor: '#fca5a5',
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
  },
  resultDetail: {
    fontSize: 13,
    color: '#1f2937',
  },
  resultPayload: {
    fontFamily: 'monospace',
    fontSize: 12,
    color: '#1f2937',
    maxHeight: 240,
  },
});
