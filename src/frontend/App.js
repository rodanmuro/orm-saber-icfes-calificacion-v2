import { StatusBar } from 'expo-status-bar';
import { useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { buildHealthUrl, getApiBaseUrl } from './src/config/api';
import { checkHealth } from './src/services/health';

export default function App() {
  const [apiBaseUrl, setApiBaseUrl] = useState(getApiBaseUrl());
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const healthUrl = useMemo(() => buildHealthUrl(apiBaseUrl), [apiBaseUrl]);

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
      </ScrollView>
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
  },
});
