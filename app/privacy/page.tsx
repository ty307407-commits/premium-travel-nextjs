import LegalPage, { generateMetadata as generateLegalMetadata } from '@/components/LegalPage';

export async function generateMetadata() {
    return generateLegalMetadata({ slug: '/privacy' });
}

export default function PrivacyPage() {
    return <LegalPage slug="/privacy" />;
}
