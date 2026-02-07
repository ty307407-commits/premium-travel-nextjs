import LegalPage, { generateMetadata as generateLegalMetadata } from '@/components/LegalPage';

export async function generateMetadata() {
    return generateLegalMetadata({ slug: '/company' });
}

export default function CompanyPage() {
    return <LegalPage slug="/company" />;
}
